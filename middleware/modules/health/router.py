from fastapi import APIRouter

from middleware.common.app_constants import APP_NAME, APP_TAGLINE

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "name": APP_NAME,
        "tagline": APP_TAGLINE,
        "message": f"{APP_NAME} API is running",
        "features": [
            "trip_compose",
            "intake_gate",
            "traveler_review",
            "local_models",
            "user_preferences",
            "jwt_auth",
        ],
    }
