import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from middleware.common.app_constants import APP_NAME
from middleware.common.log import configure_logging, get_logger
from middleware.modules.approvals_mgmt.api.router import router as approvals_router
from middleware.modules.health.api.router import router as health_router
from middleware.modules.plans_mgmt.api.router import router as plans_router
from middleware.modules.preferences_mgmt.api.router import router as preferences_router
from middleware.modules.travel_search.api.router import router as travel_search_router
from middleware.modules.user_mgmt.api.router import router as user_router
from middleware.persistence.schema_setup import upgrade_schema

load_dotenv()
logger = get_logger("api")


def apply_cors(app: FastAPI) -> None:
    raw = (os.getenv("CORS_ORIGINS") or "*").strip()
    if raw == "*":
        app.add_middleware(
            CORSMiddleware,
            allow_origin_regex=".*",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        return
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in raw.split(",") if origin.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    revision = upgrade_schema()
    logger.info("%s API ready schema=%s", APP_NAME, revision)
    yield


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title=APP_NAME,
        description=f"{APP_NAME} API for travel planning, auth, and traveler preferences.",
        version="0.1.0",
        lifespan=lifespan,
    )
    apply_cors(app)
    app.include_router(health_router)
    app.include_router(user_router)
    app.include_router(preferences_router)
    app.include_router(travel_search_router)
    app.include_router(plans_router)
    app.include_router(approvals_router)
    return app
