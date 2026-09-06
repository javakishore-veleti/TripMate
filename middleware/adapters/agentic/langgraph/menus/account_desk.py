from middleware.adapters.agentic.langgraph.dashboard.places_planner.main import resolve_job_llm
from middleware.adapters.agentic.langgraph.llm_text import complete_text
from middleware.common.default_places import PLACES_SOURCE_SYSTEM
from middleware.common.user_preferences import format_place


def run_account_desk(
    user_id: str,
    preferences: dict,
    places_source: str,
    display_name: str = "",
) -> dict:
    places = [format_place(place) for place in preferences.get("places") or []]
    provider, model, base_url = resolve_job_llm(preferences, "classify")
    state = {
        "user_id": user_id,
        "user_preferences": preferences,
        "llm_provider": provider,
        "llm_model": model,
        "llm_base_url": base_url,
    }
    source_line = (
        "built-in default places"
        if places_source == PLACES_SOURCE_SYSTEM
        else "places they saved"
    )
    note = complete_text(
        "You write a short account desk note. Two sentences. Name the place source. "
        "Mention the writing model. Do not book anything.",
        (
            f"Name: {display_name or 'traveler'}.\n"
            f"Places ({source_line}): {'; '.join(places)}.\n"
            f"Writing model: {provider} / {model or 'not set'}."
        ),
        state,
        max_tokens=160,
        job="classify",
    )
    return {
        "note": note.strip(),
        "place_count": len(places),
        "places": places,
        "places_source": places_source,
        "llm_provider": provider,
        "llm_model": model,
    }
