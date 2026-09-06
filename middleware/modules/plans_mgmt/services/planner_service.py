from overrides import override

from middleware.common.constants.travel_status import (
    TRAVEL_STATUS_AWAITING_APPROVAL,
    TRAVEL_STATUS_BLOCKED,
    TRAVEL_STATUS_COMPLETED,
    TRAVEL_STATUS_FAILED,
)
from middleware.common.dtos import TravelReqCtx, TravelRequest
from middleware.common.llm_usage import get_usage, start_usage
from middleware.core.agents.agent_names import AGENT_TRAVEL_REQUEST
from middleware.core.agents.objects import AgentsObjectFactory
from middleware.core.dao.dao_names import DAO_TRAVEL_REQUEST
from middleware.core.dao.objects import DaoObjectFactory
from middleware.core.services.interfaces import TravelPlannerService


class TravelPlannerServiceImpl(TravelPlannerService):
    @override
    def execute(self, request: TravelRequest, ctx: TravelReqCtx) -> int:
        start_usage()
        travel_dao = DaoObjectFactory.get_dao(DAO_TRAVEL_REQUEST)
        if ctx.user_id:
            if not ctx.user_preferences:
                from middleware.core.services.objects import ServicesObjectFactory
                from middleware.core.services.service_names import SERVICE_AUTH

                ctx.user_preferences = ServicesObjectFactory.get_service(
                    SERVICE_AUTH
                ).preferences_for(ctx.user_id)
            existing = travel_dao.get_for_user(ctx.user_id, ctx.thread_id)
            if existing and not ctx.user_message:
                ctx.user_message = existing.get("prompt") or ""
        code = AgentsObjectFactory.get_agent(AGENT_TRAVEL_REQUEST).execute(request, ctx)
        self._persist(request, ctx, travel_dao)
        return code

    def _persist(self, request: TravelRequest, ctx: TravelReqCtx, travel_dao) -> None:
        if not ctx.user_id:
            return
        result = dict(ctx.api_response.result or {})
        result["llm_base_url"] = ctx.llm_base_url
        ctx.api_response.result = result
        if ctx.api_response.status_code >= 500:
            status = TRAVEL_STATUS_FAILED
        elif result.get("request_accepted") is False or result.get("guardrail_allowed") is False:
            status = TRAVEL_STATUS_BLOCKED
        elif result.get("requires_approval"):
            status = TRAVEL_STATUS_AWAITING_APPROVAL
        else:
            status = TRAVEL_STATUS_COMPLETED
        travel_dao.upsert(
            {
                "thread_id": ctx.thread_id,
                "user_id": ctx.user_id,
                "prompt": ctx.user_message or request.message,
                "status": status,
                "agentic_adapter": ctx.agentic_adapter or request.agentic_adapter,
                "llm_provider": ctx.llm_provider or request.llm_provider,
                "llm_model": ctx.llm_model or request.llm_model,
                "result": result,
                "hitl": {
                    "requires_approval": bool(result.get("requires_approval")),
                    "approved": ctx.approved,
                    "feedback": ctx.feedback,
                    "approval_request": result.get("approval_request") or "",
                },
                "usage": get_usage(),
            }
        )
