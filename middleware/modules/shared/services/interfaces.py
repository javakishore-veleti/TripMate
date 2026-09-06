from abc import ABC, abstractmethod
from typing import Callable

from middleware.common.dtos import TravelReqCtx, TravelRequest


class TravelPlannerService(ABC):
    @abstractmethod
    def execute(self, request: TravelRequest, ctx: TravelReqCtx) -> int:
        raise NotImplementedError

    @abstractmethod
    def save(self, user_id: str, thread_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def cancel(self, user_id: str, thread_id: str) -> bool:
        raise NotImplementedError


class PipelineCancelService(ABC):
    @abstractmethod
    def open(self, user_id: str, thread_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def cancel(self, user_id: str, thread_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_cancelled(self, user_id: str, thread_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def bind_http(self, user_id: str, thread_id: str, session: object) -> None:
        raise NotImplementedError

    @abstractmethod
    def unbind_http(self, user_id: str, thread_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self, user_id: str, thread_id: str) -> None:
        raise NotImplementedError


class RunTraceService(ABC):
    @abstractmethod
    def open(self, user_id: str, thread_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def write(self, user_id: str, thread_id: str, line: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def since(self, user_id: str, thread_id: str, cursor: int) -> tuple[list[str], int, bool]:
        raise NotImplementedError

    @abstractmethod
    def close(self, user_id: str, thread_id: str) -> None:
        raise NotImplementedError


class DashboardPlacesService(ABC):
    @abstractmethod
    def lookup(self, user_id: str, preferences: dict, horizon: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def default_places(self) -> list[dict]:
        raise NotImplementedError


class PreferenceSkillsService(ABC):
    @abstractmethod
    def selected_names(self, user_id: str) -> list[str]:
        raise NotImplementedError


class JournalHappeningsService(ABC):
    @abstractmethod
    def lookup(
        self,
        user_id: str,
        preferences: dict,
        expand: bool = False,
        year: int | None = None,
        month: int | None = None,
    ) -> dict:
        raise NotImplementedError


class PipelineCacheService(ABC):
    @abstractmethod
    def remember(
        self,
        user_id: str,
        pipeline_key: str,
        context: dict,
        produce: Callable[[], dict],
    ) -> dict:
        raise NotImplementedError


class PlanDeskService(ABC):
    @abstractmethod
    def lookup(self, user_id: str, preferences: dict) -> dict:
        raise NotImplementedError


class PacksLensService(ABC):
    @abstractmethod
    def lookup(self, user_id: str, preferences: dict) -> dict:
        raise NotImplementedError


class AccountDeskService(ABC):
    @abstractmethod
    def lookup(self, user_id: str, preferences: dict, display_name: str = "") -> dict:
        raise NotImplementedError
