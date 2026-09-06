import json
from typing import Any

from middleware.adapters.llm_providers.objects import LLMProviderObjectFactory
from middleware.common.constants.llm_roles import LLM_ROLE_SYSTEM, LLM_ROLE_USER
from middleware.common.dtos import TravelState
from middleware.common.llm_catalog import DEFAULT_LLM_MODEL, DEFAULT_LLM_PROVIDER
from middleware.common.llm_dtos import LLMConfig, LLMMessage, LLMReqCtx, LLMRequest
from middleware.common.log import get_logger
from middleware.common.user_preferences import traveler_profile_block
from middleware.modules.preferences_mgmt.persistence.store import selected_skill_text

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


def apply_job(state: TravelState, job: str | None) -> dict:
    data = dict(state or {})
    if not job:
        return data
    chosen = (data.get("llm_jobs") or {}).get(job) or {}
    provider = str(
        chosen.get("provider") or data.get("llm_provider") or DEFAULT_LLM_PROVIDER
    ).strip() or DEFAULT_LLM_PROVIDER
    model = str(chosen.get("model") or data.get("llm_model") or DEFAULT_LLM_MODEL).strip()
    if not model:
        model = DEFAULT_LLM_MODEL
    base_url = str(chosen.get("base_url") or data.get("llm_base_url") or "").strip()
    data["llm_provider"] = provider
    data["llm_model"] = model
    data["llm_base_url"] = base_url
    return data


def complete_text(
    system_prompt: str,
    user_prompt: str,
    state: TravelState | None = None,
    max_tokens: int = SPECIALIST_MAX_TOKENS,
    job: str | None = None,
) -> str:
    state = apply_job(state or {}, job)
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
        "llm call job=%s provider=%s model=%s max_tokens=%s",
        job or "default",
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
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("The model did not return a JSON object.")
    return json.loads(text[start : end + 1])
