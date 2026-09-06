from middleware.common.dtos import TravelReqCtx, TravelRequest
from middleware.modules.shared.services.interfaces import RunTraceService, TravelPlannerService
from middleware.modules.shared.services.objects import ServicesObjectFactory
from middleware.modules.shared.services.service_names import SERVICE_RUN_TRACE, SERVICE_TRAVEL_PLANNER


class PlannerFacade:
    def __init__(
        self,
        service: TravelPlannerService | None = None,
        trace: RunTraceService | None = None,
    ):
        self._service: TravelPlannerService = service or ServicesObjectFactory.get_service(
            SERVICE_TRAVEL_PLANNER
        )
        self._trace: RunTraceService = trace or ServicesObjectFactory.get_service(SERVICE_RUN_TRACE)

    def execute(self, request: TravelRequest, ctx: TravelReqCtx) -> int:
        return self._service.execute(request, ctx)

    def save(self, user_id: str, thread_id: str) -> dict:
        return self._service.save(user_id, thread_id)

    def cancel(self, user_id: str, thread_id: str) -> bool:
        return self._service.cancel(user_id, thread_id)

    def trace_since(self, user_id: str, thread_id: str, cursor: int = 0) -> dict:
        lines, next_cursor, done = self._trace.since(user_id, thread_id, cursor)
        return {"lines": lines, "cursor": next_cursor, "done": done}
