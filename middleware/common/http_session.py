from fastapi import HTTPException, Request

from middleware.core.services.objects import ServicesObjectFactory
from middleware.core.services.service_names import SERVICE_AUTH

SESSION_COOKIE = "your_next_travel_session"
SESSION_MAX_AGE = 14 * 24 * 60 * 60


def _auth():
    return ServicesObjectFactory.get_service(SERVICE_AUTH)


def bearer_token(request: Request) -> str | None:
    header = request.headers.get("authorization") or ""
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    return token.strip()


def current_user(request: Request) -> dict | None:
    auth = _auth()
    access = bearer_token(request)
    if access:
        user = auth.user_from_access_token(access)
        if user:
            return user
    return auth.user_from_token(request.cookies.get(SESSION_COOKIE))


def require_api_user(request: Request) -> dict:
    user = current_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="Sign in required")
    return user


def set_session_cookie(response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
        path="/",
    )


def clear_session_cookie(response) -> None:
    response.delete_cookie(key=SESSION_COOKIE, path="/")
