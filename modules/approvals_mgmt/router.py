from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from common.dtos import ApprovalRequest, TravelReqCtx, TravelRequest, TravelResponse
from common.http_session import require_api_user
from common.log import get_logger
from core.services.objects import ServicesObjectFactory
from core.services.service_names import SERVICE_TRAVEL_PLANNER

router = APIRouter(tags=["approvals-mgmt"])
logger = get_logger("approvals_mgmt")


@router.post("/api/v1/travel/approve")
async def approve_travel_plan(payload: ApprovalRequest, request: Request) -> JSONResponse:
    user = require_api_user(request)
    try:
        if not payload.approved and not payload.feedback.strip():
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Please provide revision feedback when rejecting the draft.",
                },
            )
        ctx = TravelReqCtx(
            thread_id=payload.thread_id,
            approved=payload.approved,
            feedback=payload.feedback,
            user_id=user["id"],
            user_preferences=user.get("preferences") or {},
            agentic_adapter=payload.agentic_adapter,
            llm_provider=payload.llm_provider,
            llm_model=payload.llm_model,
            llm_base_url=payload.llm_base_url,
        )
        ServicesObjectFactory.get_service(SERVICE_TRAVEL_PLANNER).execute(
            TravelRequest(
                message="",
                thread_id=payload.thread_id,
                agentic_adapter=payload.agentic_adapter,
                llm_provider=payload.llm_provider,
                llm_model=payload.llm_model,
                llm_base_url=payload.llm_base_url,
            ),
            ctx,
        )
        return JSONResponse(
            content=TravelResponse(
                success=True,
                thread_id=ctx.thread_id,
                status_code=ctx.api_response.status_code,
                message=ctx.api_response.message,
                result=ctx.api_response.result,
            ).model_dump(),
        )
    except Exception as exc:
        logger.exception("approve failed thread=%s: %s", payload.thread_id, exc)
        return JSONResponse(
            content=TravelResponse(
                success=False,
                thread_id=payload.thread_id,
                status_code=500,
                message=str(exc),
                result={},
            ).model_dump(),
            status_code=500,
        )
