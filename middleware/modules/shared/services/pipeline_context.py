from datetime import date
from typing import Callable

from middleware.common.default_places import preferences_for_pipeline
from middleware.common.popular_events import attach_nearby_events, months_for_horizon
from middleware.common.user_preferences import format_place

_MODEL_HINTS = (
    "No local Ollama model is available",
    "No Ollama model selected",
    "Ollama is not reachable",
    "Pick a model on your account first",
)


def is_model_config_error(exc: BaseException | str) -> bool:
    text = str(exc)
    return any(hint in text for hint in _MODEL_HINTS)


def remember_menu(
    cache,
    user_id: str,
    pipeline_key: str,
    context: dict,
    produce: Callable[[], dict],
) -> dict:
    try:
        return cache.remember(user_id, pipeline_key, context, produce)
    except (ValueError, RuntimeError) as exc:
        if not is_model_config_error(exc):
            raise
        return {"needs_model": True}


def pipeline_prefs(preferences: dict | None) -> tuple[dict, str, list[str]]:
    prefs, source = preferences_for_pipeline(preferences)
    labels = [format_place(place) for place in prefs["places"]]
    return prefs, source, labels


def menu_context(
    menu: str,
    prefs: dict,
    source: str,
    extra: dict | None = None,
    packs: list[str] | None = None,
) -> dict:
    context = {
        "menu": menu,
        "places": [format_place(place) for place in prefs.get("places") or []],
        "places_source": source,
        "radius": prefs.get("event_radius_miles"),
        "packs": list(packs or []),
        "llm_provider": prefs.get("llm_provider") or "",
        "llm_model": prefs.get("llm_model") or "",
    }
    if extra:
        context.update(extra)
    return context


def catalog_fallback(
    preferences: dict | None,
    months: list[int] | int | None = None,
    limit: int = 5,
    extra: dict | None = None,
) -> dict:
    _prefs, source, labels = pipeline_prefs(preferences)
    payload = attach_nearby_events(
        {"needs_model": True, "places": labels, "places_source": source},
        labels,
        months if months is not None else date.today().month,
        limit,
    )
    payload["places_source"] = source
    if extra:
        payload.update(extra)
    return payload


def dashboard_catalog_fallback(preferences: dict | None, horizon: str) -> dict:
    return catalog_fallback(preferences, months_for_horizon(horizon), limit=8)
