from abc import ABC, abstractmethod

from middleware.common.dtos import TravelReqCtx, TravelRequest


class TravelPlannerService(ABC):
    @abstractmethod
    def execute(self, request: TravelRequest, ctx: TravelReqCtx) -> int:
        raise NotImplementedError


class DashboardPlacesService(ABC):
    @abstractmethod
    def lookup(self, user_id: str, preferences: dict, horizon: str) -> dict:
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
