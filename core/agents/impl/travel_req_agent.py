from overrides import override

from adapters.agentic.objects import AgenticAdapterObjectFactory
from core.agents.agent_interfaces import TravelAgent
from common.app_constants import ResponseCode
from common.dtos import TravelReqCtx, TravelRequest
from common.log import get_logger

logger = get_logger(__name__)


class TravelRequestAgentImpl(TravelAgent[TravelRequest, TravelReqCtx]):
    @override
    def execute(self, request: TravelRequest, ctx: TravelReqCtx) -> int:
        ctx.user_message = request.message.strip() or ctx.user_message
        if not ctx.user_message and not ctx.approved and not ctx.feedback.strip():
            logger.info("travel request skipped thread=%s", ctx.thread_id)
            return ResponseCode.SKIP
        ctx.agentic_adapter = request.agentic_adapter
        ctx.llm_provider = request.llm_provider
        ctx.llm_model = request.llm_model
        ctx.llm_base_url = request.llm_base_url
        logger.info(
            "handoff adapter=%s thread=%s approved=%s",
            request.agentic_adapter,
            ctx.thread_id,
            ctx.approved,
        )
        return AgenticAdapterObjectFactory.get_agentic_adapter(
            request.agentic_adapter
        ).execute(request, ctx)
