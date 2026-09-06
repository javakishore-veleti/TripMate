from middleware.adapters.agentic.langgraph.dashboard.places_planner.main import resolve_job_llm
from middleware.adapters.agentic.langgraph.llm_text import complete_text
from middleware.common.user_preferences import format_place


def _clip(text: str, limit: int) -> str:
    cleaned = " ".join((text or "").split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rsplit(" ", 1)[0] + "…"


def run_plan_desk(
    user_id: str,
    preferences: dict,
    leftover_line: str = "",
    skill_names: list[str] | None = None,
) -> dict:
    places = [format_place(place) for place in preferences.get("places") or []]
    provider, model, base_url = resolve_job_llm(preferences, "reason")
    state = {
        "user_id": user_id,
        "user_preferences": preferences,
        "llm_provider": provider,
        "llm_model": model,
        "llm_base_url": base_url,
    }
    leftover = leftover_line.strip()
    packs = ", ".join(skill_names or []) or "no packs selected"
    note = complete_text(
        "Write one short sentence for a trip desk. No brochure. No sights list. "
        "No instructions. Do not book anything.",
        (
            f"Places: {'; '.join(places) or 'none'}.\n"
            f"Packs: {packs}.\n"
            f"Last ask: {_clip(leftover, 80) or 'none'}."
        ),
        state,
        max_tokens=60,
        job="reason",
    )
    return {
        "headline": "Your next ask",
        "note": _clip(note, 140),
        "leftover": _clip(leftover, 80),
        "places": places,
        "skill_names": list(skill_names or []),
        "llm_provider": provider,
        "llm_model": model,
    }
