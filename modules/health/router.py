from fastapi import APIRouter

from common.app_constants import APP_NAME, APP_TAGLINE

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "name": APP_NAME,
        "tagline": APP_TAGLINE,
        "message": f"{APP_NAME} API is running",
        "features": [
            "supervisor_agent",
            "input_guardrail",
            "human_in_the_loop",
            "ollama_provider",
            "user_preferences",
            "jwt_auth",
        ],
    }
