from middleware.common.dtos import TravelReqCtx, TravelRequest
from middleware.modules.shared.services.objects import ServicesObjectFactory
from middleware.modules.shared.services.service_names import SERVICE_TRAVEL_PLANNER


class PlannerFacade:
    def __init__(self):
        self._service = ServicesObjectFactory.get_service(SERVICE_TRAVEL_PLANNER)

    def execute(self, request: TravelRequest, ctx: TravelReqCtx) -> int:
        return self._service.execute(request, ctx)
