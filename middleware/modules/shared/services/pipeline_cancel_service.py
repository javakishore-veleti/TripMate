import threading
from contextvars import ContextVar

from overrides import override

from middleware.modules.shared.services.interfaces import PipelineCancelService

_run_user: ContextVar[str] = ContextVar("pipeline_cancel_user", default="")
_run_thread: ContextVar[str] = ContextVar("pipeline_cancel_thread", default="")


class PipelineCancelled(Exception):
    """Raised when the traveler stops a draft mid-pipeline."""


class PipelineCancelServiceImpl(PipelineCancelService):
    def __init__(self) -> None:
        self._events: dict[tuple[str, str], threading.Event] = {}
        self._http: dict[tuple[str, str], object] = {}
        self._lock = threading.Lock()

    def _key(self, user_id: str, thread_id: str) -> tuple[str, str]:
        return (user_id, thread_id)

    @override
    def open(self, user_id: str, thread_id: str) -> None:
        key = self._key(user_id, thread_id)
        with self._lock:
            if key not in self._events:
                self._events[key] = threading.Event()

    @override
    def cancel(self, user_id: str, thread_id: str) -> bool:
        key = self._key(user_id, thread_id)
        with self._lock:
            event = self._events.get(key)
            if event is None:
                event = threading.Event()
                self._events[key] = event
            event.set()
            session = self._http.get(key)
        closer = getattr(session, "close", None)
        if callable(closer):
            closer()
        return True

    @override
    def is_cancelled(self, user_id: str, thread_id: str) -> bool:
        with self._lock:
            event = self._events.get(self._key(user_id, thread_id))
        return bool(event and event.is_set())

    @override
    def bind_http(self, user_id: str, thread_id: str, session: object) -> None:
        with self._lock:
            self._http[self._key(user_id, thread_id)] = session

    @override
    def unbind_http(self, user_id: str, thread_id: str) -> None:
        with self._lock:
            self._http.pop(self._key(user_id, thread_id), None)

    @override
    def close(self, user_id: str, thread_id: str) -> None:
        key = self._key(user_id, thread_id)
        with self._lock:
            self._events.pop(key, None)
            self._http.pop(key, None)


def bind_cancel(user_id: str, thread_id: str):
    return _run_user.set(user_id), _run_thread.set(thread_id)


def unbind_cancel(user_token, thread_token) -> None:
    _run_user.reset(user_token)
    _run_thread.reset(thread_token)


def current_run() -> tuple[str, str]:
    return _run_user.get(), _run_thread.get()


def raise_if_cancelled() -> None:
    user_id, thread_id = current_run()
    if not user_id or not thread_id:
        return
    from middleware.modules.shared.services.objects import ServicesObjectFactory
    from middleware.modules.shared.services.service_names import SERVICE_PIPELINE_CANCEL

    if ServicesObjectFactory.get_service(SERVICE_PIPELINE_CANCEL).is_cancelled(user_id, thread_id):
        raise PipelineCancelled()
