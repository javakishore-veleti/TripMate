import secrets
import string
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from middleware.common.dtos import (
    DELETE_TRAVEL_PLAN_PHRASE,
    DeleteTravelRequest,
    JournalHappeningsRequest,
    TravelReqCtx,
    TravelRequest,
    TravelResponse,
)
from middleware.common.http_session import require_api_user
from middleware.common.log import get_logger, preview
from middleware.core.dao.dao_names import DAO_TRAVEL_REQUEST
from middleware.core.dao.objects import DaoObjectFactory
from middleware.modules.plans_mgmt.facades.happenings_facade import HappeningsFacade
from middleware.modules.plans_mgmt.facades.planner_facade import PlannerFacade

router = APIRouter(tags=["plans-mgmt"])
logger = get_logger("plans_mgmt")
_THREAD_ID_ALPHABET = string.ascii_letters + string.digits


def new_thread_id() -> str:
    suffix = "".join(secrets.choice(_THREAD_ID_ALPHABET) for _ in range(10))
    return f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{suffix}"


def resolve_thread_id(raw: str | None) -> str:
    if raw and raw.strip().lower() not in {"undefined", "null", "none"}:
        return raw.strip()
    return new_thread_id()


@router.post("/api/v1/journal/happenings")
async def journal_happenings(payload: JournalHappeningsRequest, request: Request):
    user = require_api_user(request)
    try:
        result = HappeningsFacade().lookup(
            user_id=user["id"],
            preferences=user.get("preferences") or {},
            expand=payload.expand,
            year=payload.year,
            month=payload.month,
        )
        return {"success": True, **result}
    except ValueError as exc:
        return JSONResponse(
            {"success": False, "message": str(exc), "events": []},
            status_code=400,
        )
    except Exception as exc:
        logger.exception("journal happenings failed: %s", exc)
        return JSONResponse(
            {"success": False, "message": str(exc), "events": []},
            status_code=502,
        )


@router.get("/api/v1/travel/requests")
async def list_travel_requests(request: Request):
    user = require_api_user(request)
    records = DaoObjectFactory.get_dao(DAO_TRAVEL_REQUEST).list_for_user(user["id"])
    return {"success": True, "requests": records}


@router.get("/api/v1/travel/requests/{thread_id}")
async def get_travel_request(thread_id: str, request: Request):
    user = require_api_user(request)
    record = DaoObjectFactory.get_dao(DAO_TRAVEL_REQUEST).get_for_user(user["id"], thread_id)
    if record is None:
        return JSONResponse({"success": False, "message": "Request not found"}, status_code=404)
    return {"success": True, "request": record}


@router.delete("/api/v1/travel/requests/{thread_id}")
async def delete_travel_request(thread_id: str, payload: DeleteTravelRequest, request: Request):
    user = require_api_user(request)
    if payload.confirmation.strip().lower() != DELETE_TRAVEL_PLAN_PHRASE:
        return JSONResponse(
            {
                "success": False,
                "message": f'Type "{DELETE_TRAVEL_PLAN_PHRASE}" to delete this travel plan.',
            },
            status_code=400,
        )
    dao = DaoObjectFactory.get_dao(DAO_TRAVEL_REQUEST)
    if not dao.delete_for_user_thread(user["id"], thread_id):
        return JSONResponse({"success": False, "message": "Travel plan not found."}, status_code=404)
    logger.info("travel plan deleted thread=%s user=%s", thread_id, user["id"])
    return {"success": True}


@router.post("/api/v1/travel/planner")
async def travel_planner(payload: TravelRequest, request: Request) -> JSONResponse:
    user = require_api_user(request)
    try:
        thread_id = resolve_thread_id(payload.thread_id)
        ctx = TravelReqCtx(
            thread_id=thread_id,
            approved=False,
            user_id=user["id"],
            user_preferences=user.get("preferences") or {},
            llm_provider=payload.llm_provider,
            llm_model=payload.llm_model,
            llm_base_url=payload.llm_base_url,
            agentic_adapter=payload.agentic_adapter,
        )
        logger.info(
            "planner start thread=%s adapter=%s provider=%s model=%s url=%s prompt=%s",
            thread_id,
            payload.agentic_adapter,
            payload.llm_provider,
            payload.llm_model,
            payload.llm_base_url or "-",
            preview(payload.message),
        )
        PlannerFacade().execute(payload, ctx)
        result = dict(ctx.api_response.result or {})
        if ctx.user_message:
            result["prompt"] = ctx.user_message
        return JSONResponse(
            content=TravelResponse(
                success=True,
                thread_id=ctx.thread_id,
                status_code=ctx.api_response.status_code,
                message=ctx.api_response.message,
                result=result,
            ).model_dump(),
        )
    except Exception as exc:
        logger.exception("planner failed: %s", exc)
        return JSONResponse(
            content=TravelResponse(
                success=False,
                message=str(exc),
                status_code=500,
                result={},
            ).model_dump(),
            status_code=500,
        )
