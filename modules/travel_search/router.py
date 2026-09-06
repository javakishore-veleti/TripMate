from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from common.dtos import AreaEventsRequest
from common.http_session import require_api_user
from common.llm_catalog import ui_catalog
from core.services.objects import ServicesObjectFactory
from core.services.service_names import SERVICE_DASHBOARD_PLACES

router = APIRouter(tags=["travel-search"])


@router.get("/api/v1/llm/catalog")
async def llm_catalog(base_url: str | None = None):
    return ui_catalog(ollama_url=base_url)


@router.post("/api/v1/area-events")
async def area_events(payload: AreaEventsRequest, request: Request):
    user = require_api_user(request)
    try:
        result = ServicesObjectFactory.get_service(SERVICE_DASHBOARD_PLACES).lookup(
            user_id=user["id"],
            preferences=user.get("preferences") or {},
            horizon=payload.horizon,
        )
        return {"success": True, **result}
    except ValueError as exc:
        return JSONResponse({"success": False, "message": str(exc), "events": []}, status_code=400)
    except Exception as exc:
        return JSONResponse(
            {"success": False, "message": str(exc), "events": []},
            status_code=502,
        )
