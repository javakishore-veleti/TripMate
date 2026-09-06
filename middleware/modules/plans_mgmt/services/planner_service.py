import logging

from overrides import override

from middleware.common.constants.travel_status import (
    TRAVEL_STATUS_AWAITING_APPROVAL,
    TRAVEL_STATUS_BLOCKED,
    TRAVEL_STATUS_CANCELLED,
    TRAVEL_STATUS_COMPLETED,
    TRAVEL_STATUS_FAILED,
)
from middleware.common.dtos import TravelReqCtx, TravelRequest
from middleware.common.llm_usage import get_usage, start_usage
from middleware.core.agents.agent_names import AGENT_TRAVEL_REQUEST
from middleware.core.agents.objects import AgentsObjectFactory
from middleware.modules.shared.persistence.dao.dao_names import DAO_DRAFT_PLAN, DAO_TRAVEL_REQUEST
from middleware.modules.shared.persistence.dao.objects import DaoObjectFactory
from middleware.common.log import LOGGER_NAME, get_logger
from middleware.modules.plans_mgmt.persistence.interfaces import DraftPlanDao, TravelRequestDao
from middleware.modules.shared.services.interfaces import (
    PipelineCancelService,
    RunTraceService,
    TravelPlannerService,
)
from middleware.modules.shared.services.pipeline_cancel_service import (
    PipelineCancelled,
    bind_cancel,
    unbind_cancel,
)
from middleware.modules.shared.services.run_trace_service import (
    TraceLogHandler,
    bind_trace,
    unbind_trace,
)
from middleware.modules.shared.services.service_names import SERVICE_PIPELINE_CANCEL, SERVICE_RUN_TRACE


class TravelPlannerServiceImpl(TravelPlannerService):
    def __init__(
        self,
        trace: RunTraceService | None = None,
        drafts: DraftPlanDao | None = None,
        travel_requests: TravelRequestDao | None = None,
    ):
        self._trace = trace
        self._drafts = drafts
        self._travel_requests = travel_requests

    def _trace_service(self) -> RunTraceService:
        if self._trace is not None:
            return self._trace
        from middleware.modules.shared.services.objects import ServicesObjectFactory

        return ServicesObjectFactory.get_service(SERVICE_RUN_TRACE)

    def _cancel_service(self) -> PipelineCancelService:
        from middleware.modules.shared.services.objects import ServicesObjectFactory

        return ServicesObjectFactory.get_service(SERVICE_PIPELINE_CANCEL)

    def _draft_dao(self) -> DraftPlanDao:
        if self._drafts is not None:
            return self._drafts
        return DaoObjectFactory.get_dao(DAO_DRAFT_PLAN)

    def _travel_dao(self) -> TravelRequestDao:
        if self._travel_requests is not None:
            return self._travel_requests
        return DaoObjectFactory.get_dao(DAO_TRAVEL_REQUEST)

    @override
    def execute(self, request: TravelRequest, ctx: TravelReqCtx) -> int:
        start_usage()
        draft_dao = self._draft_dao()
        travel_dao = self._travel_dao()
        if ctx.user_id:
            if not ctx.user_preferences:
                from middleware.modules.shared.services.objects import ServicesObjectFactory
                from middleware.modules.shared.services.service_names import SERVICE_AUTH

                ctx.user_preferences = ServicesObjectFactory.get_service(
                    SERVICE_AUTH
                ).preferences_for(ctx.user_id)
            existing = draft_dao.get_for_user(ctx.user_id, ctx.thread_id) or travel_dao.get_for_user(
                ctx.user_id, ctx.thread_id
            )
            if existing and not ctx.user_message:
                ctx.user_message = existing.get("prompt") or ""
        trace = self._trace_service()
        cancel = self._cancel_service()
        handler = None
        tokens = None
        cancel_tokens = None
        if ctx.user_id and ctx.thread_id:
            trace.open(ctx.user_id, ctx.thread_id)
            cancel.open(ctx.user_id, ctx.thread_id)
            handler = TraceLogHandler(trace, ctx.user_id, ctx.thread_id)
            handler.setFormatter(logging.Formatter("%(message)s"))
            tokens = bind_trace(ctx.user_id, ctx.thread_id)
            cancel_tokens = bind_cancel(ctx.user_id, ctx.thread_id)
            get_logger(LOGGER_NAME).addHandler(handler)
        try:
            code = AgentsObjectFactory.get_agent(AGENT_TRAVEL_REQUEST).execute(request, ctx)
            self._write_draft(request, ctx, draft_dao)
            return code
        except PipelineCancelled:
            result = dict(ctx.api_response.result or {})
            result["cancelled"] = True
            result["request_accepted"] = False
            result["request_note"] = "You stopped this draft."
            ctx.api_response.result = result
            ctx.api_response.message = "Draft cancelled."
            self._write_draft(request, ctx, draft_dao)
            return 200
        finally:
            if ctx.user_id and ctx.thread_id:
                if handler:
                    get_logger(LOGGER_NAME).removeHandler(handler)
                if tokens:
                    unbind_trace(*tokens)
                if cancel_tokens:
                    unbind_cancel(*cancel_tokens)
                cancel.close(ctx.user_id, ctx.thread_id)
                trace.close(ctx.user_id, ctx.thread_id)

    @override
    def save(self, user_id: str, thread_id: str) -> dict:
        draft = self._draft_dao().get_for_user(user_id, thread_id)
        if draft is None:
            raise ValueError("There is no draft to save.")
        saved = self._travel_dao().upsert(
            {
                "thread_id": draft["thread_id"],
                "user_id": user_id,
                "prompt": draft.get("prompt") or "",
                "status": draft.get("status") or TRAVEL_STATUS_COMPLETED,
                "agentic_adapter": draft.get("agentic_adapter") or "",
                "llm_provider": draft.get("llm_provider") or "",
                "llm_model": draft.get("llm_model") or "",
                "result": draft.get("result") or {},
                "hitl": draft.get("hitl") or {},
                "usage": draft.get("usage") or {},
            }
        )
        self._draft_dao().delete_for_user_thread(user_id, thread_id)
        return saved

    @override
    def cancel(self, user_id: str, thread_id: str) -> bool:
        return self._cancel_service().cancel(user_id, thread_id)

    def _write_draft(self, request: TravelRequest, ctx: TravelReqCtx, draft_dao: DraftPlanDao) -> None:
        if not ctx.user_id:
            return
        result = dict(ctx.api_response.result or {})
        result["llm_base_url"] = ctx.llm_base_url
        ctx.api_response.result = result
        if ctx.api_response.status_code >= 500:
            status = TRAVEL_STATUS_FAILED
        elif result.get("cancelled"):
            status = TRAVEL_STATUS_CANCELLED
        elif result.get("request_accepted") is False or result.get("guardrail_allowed") is False:
            status = TRAVEL_STATUS_BLOCKED
        elif result.get("requires_approval"):
            status = TRAVEL_STATUS_AWAITING_APPROVAL
        else:
            status = TRAVEL_STATUS_COMPLETED
        draft_dao.upsert(
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
