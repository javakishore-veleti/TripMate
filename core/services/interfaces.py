from abc import ABC, abstractmethod

from common.dtos import TravelReqCtx, TravelRequest


class TravelPlannerService(ABC):
    @abstractmethod
    def execute(self, request: TravelRequest, ctx: TravelReqCtx) -> int:
        raise NotImplementedError


class DashboardPlacesService(ABC):
    @abstractmethod
    def lookup(self, user_id: str, preferences: dict, horizon: str) -> dict:
        raise NotImplementedError
