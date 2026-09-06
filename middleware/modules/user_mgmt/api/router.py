from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from middleware.common.dtos import SigninRequest, SignupRequest, UserPreferencesRequest
from middleware.common.http_session import (
    SESSION_COOKIE,
    clear_session_cookie,
    require_api_user,
    set_session_cookie,
)
from middleware.modules.shared.services.pipeline_context import is_model_config_error
from middleware.modules.user_mgmt.facades.account_desk_facade import AccountDeskFacade
from middleware.modules.user_mgmt.facades.auth_facade import AuthFacade

router = APIRouter(tags=["user-mgmt"])


def _auth():
    return AuthFacade()


def _auth_payload(user: dict) -> dict:
    return {
        "success": True,
        "user": user,
        "access_token": _auth().issue_access_token(user),
        "token_type": "bearer",
    }


@router.post("/api/v1/auth/signup")
async def signup(payload: SignupRequest):
    try:
        user = _auth().signup(payload.email, payload.password, payload.display_name)
        response = JSONResponse(_auth_payload(user))
        set_session_cookie(response, _auth().create_session(user["id"]))
        return response
    except ValueError as exc:
        return JSONResponse({"success": False, "message": str(exc)}, status_code=400)


@router.post("/api/v1/auth/signin")
async def signin(payload: SigninRequest):
    try:
        user = _auth().signin(payload.email, payload.password)
        response = JSONResponse(_auth_payload(user))
        set_session_cookie(response, _auth().create_session(user["id"]))
        return response
    except ValueError as exc:
        return JSONResponse({"success": False, "message": str(exc)}, status_code=400)


@router.post("/api/v1/auth/signout")
async def signout(request: Request):
    _auth().signout(request.cookies.get(SESSION_COOKIE))
    response = JSONResponse({"success": True})
    clear_session_cookie(response)
    return response


@router.get("/api/v1/auth/me")
async def me(request: Request):
    user = require_api_user(request)
    return {
        "success": True,
        "user": user,
        "access_token": _auth().issue_access_token(user),
        "token_type": "bearer",
    }


@router.delete("/api/v1/auth/account")
async def delete_account(request: Request):
    user = require_api_user(request)
    _auth().delete_account(user["id"])
    response = JSONResponse({"success": True})
    clear_session_cookie(response)
    return response


@router.post("/api/v1/account/desk")
async def account_desk(request: Request):
    user = require_api_user(request)
    try:
        result = AccountDeskFacade().lookup(
            user_id=user["id"],
            preferences=user.get("preferences") or {},
            display_name=user.get("display_name") or "",
        )
        return {"success": True, **result}
    except ValueError as exc:
        if is_model_config_error(exc):
            return {"success": True, "needs_model": True}
        return JSONResponse({"success": False, "message": str(exc)}, status_code=400)
    except Exception as exc:
        if is_model_config_error(exc):
            return {"success": True, "needs_model": True}
        return JSONResponse({"success": False, "message": str(exc)}, status_code=502)


@router.get("/api/v1/preferences")
async def get_preferences(request: Request):
    user = require_api_user(request)
    return {"success": True, "preferences": user["preferences"]}


@router.put("/api/v1/preferences")
async def put_preferences(payload: UserPreferencesRequest, request: Request):
    user = require_api_user(request)
    updated = _auth().save_preferences(user["id"], payload.model_dump())
    return {"success": True, "user": updated, "preferences": updated["preferences"]}
