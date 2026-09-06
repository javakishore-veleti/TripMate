from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from middleware.common.dtos import PreferenceSkillRequest, PreferenceSkillSelectRequest
from middleware.common.http_session import require_api_user
from middleware.modules.preferences_mgmt.facades.preferences_facade import PreferencesFacade

router = APIRouter(tags=["preferences-mgmt"])
_prefs = PreferencesFacade()


@router.get("/api/v1/preference-skills")
async def list_preference_skills(request: Request):
    user = require_api_user(request)
    return {"success": True, "skills": _prefs.list_skills(user["id"]), "max_selected": _prefs.max_selected}


@router.get("/api/v1/preference-skills/{slug}")
async def get_preference_skill(slug: str, request: Request):
    user = require_api_user(request)
    skill = _prefs.get_skill(user["id"], slug)
    if skill is None:
        return JSONResponse({"success": False, "message": "Preference not found"}, status_code=404)
    return {"success": True, "skill": skill}


@router.post("/api/v1/preference-skills")
async def create_preference_skill(payload: PreferenceSkillRequest, request: Request):
    user = require_api_user(request)
    if not payload.name.strip():
        return JSONResponse({"success": False, "message": "Give this preference a name."}, status_code=400)
    try:
        skill = _prefs.create_skill(
            user["id"],
            payload.name,
            payload.description,
            payload.sections.model_dump(),
        )
        return {"success": True, "skill": skill}
    except ValueError as exc:
        return JSONResponse({"success": False, "message": str(exc)}, status_code=400)


@router.put("/api/v1/preference-skills/{slug}")
async def update_preference_skill(slug: str, payload: PreferenceSkillRequest, request: Request):
    user = require_api_user(request)
    if not payload.name.strip():
        return JSONResponse({"success": False, "message": "Give this preference a name."}, status_code=400)
    try:
        skill = _prefs.update_skill(
            user["id"],
            slug,
            payload.name,
            payload.description,
            payload.sections.model_dump(),
        )
        return {"success": True, "skill": skill}
    except ValueError as exc:
        status = 404 if "not found" in str(exc).lower() else 400
        return JSONResponse({"success": False, "message": str(exc)}, status_code=status)


@router.delete("/api/v1/preference-skills/{slug}")
async def delete_preference_skill(slug: str, request: Request):
    user = require_api_user(request)
    try:
        _prefs.delete_skill(user["id"], slug)
        return {"success": True}
    except ValueError as exc:
        return JSONResponse({"success": False, "message": str(exc)}, status_code=404)


@router.put("/api/v1/preference-skills-selection")
async def select_preference_skills(payload: PreferenceSkillSelectRequest, request: Request):
    user = require_api_user(request)
    try:
        selected = _prefs.set_selected(user["id"], payload.ids)
        return {"success": True, "ids": selected, "max_selected": _prefs.max_selected}
    except ValueError as exc:
        return JSONResponse({"success": False, "message": str(exc)}, status_code=400)
