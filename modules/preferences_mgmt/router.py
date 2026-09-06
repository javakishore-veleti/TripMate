from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from common.dtos import PreferenceSkillRequest, PreferenceSkillSelectRequest
from common.http_session import require_api_user
from modules.preferences_mgmt import store

router = APIRouter(tags=["preferences-mgmt"])


@router.get("/api/v1/preference-skills")
async def list_preference_skills(request: Request):
    user = require_api_user(request)
    return {"success": True, "skills": store.list_skills(user["id"]), "max_selected": store.MAX_SELECTED}


@router.get("/api/v1/preference-skills/{slug}")
async def get_preference_skill(slug: str, request: Request):
    user = require_api_user(request)
    skill = store.get_skill(user["id"], slug)
    if skill is None:
        return JSONResponse({"success": False, "message": "Preference not found"}, status_code=404)
    return {"success": True, "skill": skill}


@router.post("/api/v1/preference-skills")
async def create_preference_skill(payload: PreferenceSkillRequest, request: Request):
    user = require_api_user(request)
    if not payload.name.strip():
        return JSONResponse({"success": False, "message": "Give this preference a name."}, status_code=400)
    try:
        skill = store.create_skill(
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
        skill = store.update_skill(
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
        store.delete_skill(user["id"], slug)
        return {"success": True}
    except ValueError as exc:
        return JSONResponse({"success": False, "message": str(exc)}, status_code=404)


@router.put("/api/v1/preference-skills-selection")
async def select_preference_skills(payload: PreferenceSkillSelectRequest, request: Request):
    user = require_api_user(request)
    try:
        selected = store.set_selected(user["id"], payload.ids)
        return {"success": True, "ids": selected, "max_selected": store.MAX_SELECTED}
    except ValueError as exc:
        return JSONResponse({"success": False, "message": str(exc)}, status_code=400)
