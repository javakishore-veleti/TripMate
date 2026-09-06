import logging
import threading
from contextvars import ContextVar

from overrides import override

from middleware.modules.shared.services.interfaces import RunTraceService

_MAX_LINES = 400
_trace_user: ContextVar[str] = ContextVar("run_trace_user", default="")
_trace_thread: ContextVar[str] = ContextVar("run_trace_thread", default="")


class _Buffer:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.done = False
        self.lock = threading.Lock()

    def append(self, line: str) -> None:
        with self.lock:
            self.lines.append(line)
            if len(self.lines) > _MAX_LINES:
                self.lines = self.lines[-_MAX_LINES:]

    def close(self) -> None:
        with self.lock:
            self.done = True

    def since(self, cursor: int) -> tuple[list[str], int, bool]:
        with self.lock:
            start = max(0, min(cursor, len(self.lines)))
            return self.lines[start:], len(self.lines), self.done


class RunTraceServiceImpl(RunTraceService):
    def __init__(self) -> None:
        self._buffers: dict[tuple[str, str], _Buffer] = {}
        self._lock = threading.Lock()

    def _key(self, user_id: str, thread_id: str) -> tuple[str, str]:
        return (user_id, thread_id)

    @override
    def open(self, user_id: str, thread_id: str) -> None:
        with self._lock:
            self._buffers[self._key(user_id, thread_id)] = _Buffer()

    @override
    def write(self, user_id: str, thread_id: str, line: str) -> None:
        with self._lock:
            buf = self._buffers.get(self._key(user_id, thread_id))
        if buf:
            buf.append(line)

    @override
    def since(self, user_id: str, thread_id: str, cursor: int) -> tuple[list[str], int, bool]:
        with self._lock:
            buf = self._buffers.get(self._key(user_id, thread_id))
        if buf is None:
            return [], 0, False
        return buf.since(cursor)

    @override
    def close(self, user_id: str, thread_id: str) -> None:
        with self._lock:
            buf = self._buffers.get(self._key(user_id, thread_id))
        if buf:
            buf.close()


class TraceLogHandler(logging.Handler):
    def __init__(self, service: RunTraceService, user_id: str, thread_id: str) -> None:
        super().__init__()
        self._service = service
        self._user_id = user_id
        self._thread_id = thread_id

    def emit(self, record: logging.LogRecord) -> None:
        if not self._user_id or not self._thread_id:
            return
        try:
            line = self.format(record)
        except Exception:
            line = record.getMessage()
        self._service.write(self._user_id, self._thread_id, line)


def bind_trace(user_id: str, thread_id: str):
    return _trace_user.set(user_id), _trace_thread.set(thread_id)


def unbind_trace(user_token, thread_token) -> None:
    _trace_user.reset(user_token)
    _trace_thread.reset(thread_token)
