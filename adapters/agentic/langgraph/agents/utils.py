import json
from typing import Any

from adapters.llm_providers.objects import LLMProviderObjectFactory
from common.constants.llm_roles import LLM_ROLE_SYSTEM, LLM_ROLE_USER
from common.dtos import TravelState
from common.llm_catalog import DEFAULT_LLM_MODEL, DEFAULT_LLM_PROVIDER
from common.llm_dtos import LLMConfig, LLMMessage, LLMReqCtx, LLMRequest
from common.log import get_logger
from common.user_preferences import traveler_profile_block
from modules.preferences_mgmt.store import selected_skill_text

logger = get_logger(__name__)

JSON_MAX_TOKENS = 400
SPECIALIST_MAX_TOKENS = 700
PLAN_MAX_TOKENS = 1200
CLIP_CHARS = 1200


def empty_constraints() -> dict[str, Any]:
    return {
        "destination": "",
        "origin": "",
        "duration": "",
        "budget": "",
        "travel_style": "",
        "special_preferences": [],
    }


def llm_text(request: LLMRequest, ctx: LLMReqCtx) -> str:
    ctx.request = request
    provider = LLMProviderObjectFactory.get_provider(request)
    return provider.complete(request, ctx).text


def clip_text(text: Any, limit: int = CLIP_CHARS) -> str:
    value = str(text or "").strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1] + "…"


def specialist_notes(state: TravelState) -> dict[str, str]:
    return {
        "flights": clip_text(state.get("flight_results")),
        "hotels": clip_text(state.get("hotel_results")),
        "weather": clip_text(state.get("weather_results")),
        "budget": clip_text(state.get("budget_results")),
        "itinerary": clip_text(state.get("itinerary"), CLIP_CHARS * 2),
    }


def complete_text(
    system_prompt: str,
    user_prompt: str,
    state: TravelState | None = None,
    max_tokens: int = SPECIALIST_MAX_TOKENS,
) -> str:
    state = state or {}
    profile = traveler_profile_block(state.get("user_preferences"))
    skills = selected_skill_text(str(state.get("user_id") or ""))
    system = system_prompt.strip()
    extras = [block for block in (profile, skills) if block]
    if extras:
        system = f"{system}\n\n" + "\n\n".join(extras)
    request = LLMRequest(
        messages=[
            LLMMessage(role=LLM_ROLE_SYSTEM, content=system),
            LLMMessage(role=LLM_ROLE_USER, content=user_prompt),
        ],
        provider=str(state.get("llm_provider") or DEFAULT_LLM_PROVIDER),
        config=LLMConfig(
            model=str(state.get("llm_model") or DEFAULT_LLM_MODEL),
            max_tokens=max_tokens,
            base_url=str(state.get("llm_base_url") or "") or None,
        ),
    )
    logger.info(
        "llm call provider=%s model=%s max_tokens=%s",
        request.provider,
        request.config.model,
        max_tokens,
    )
    return llm_text(request, LLMReqCtx(request=request))


def destination_from_state(state: TravelState) -> str:
    constraints = state.get("trip_constraints") or {}
    destination = str(constraints.get("destination") or "").strip()
    return destination or str(state.get("user_query") or "").strip()


def json_from_llm(text: str) -> dict[str, Any]:
    """Extract the first complete JSON object returned by the model."""
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError("The model did not return a JSON object.")

    return json.loads(text[start : end + 1])
