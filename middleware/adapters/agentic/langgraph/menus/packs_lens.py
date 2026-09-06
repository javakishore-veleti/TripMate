from middleware.adapters.agentic.langgraph.dashboard.places_planner.main import resolve_job_llm
from middleware.adapters.agentic.langgraph.llm_text import complete_text


def run_packs_lens(user_id: str, preferences: dict, skill_names: list[str] | None = None) -> dict:
    provider, model, base_url = resolve_job_llm(preferences, "classify")
    state = {
        "user_id": user_id,
        "user_preferences": preferences,
        "llm_provider": provider,
        "llm_model": model,
        "llm_base_url": base_url,
    }
    packs = ", ".join(skill_names or []) or "no packs selected yet"
    note = complete_text(
        "You explain in one short paragraph how selected travel packs will color the next trip draft. "
        "Plain sentences. No booking. No sales tone.",
        f"Selected packs: {packs}.",
        state,
        max_tokens=180,
        job="classify",
    )
    return {
        "note": note.strip(),
        "skill_names": list(skill_names or []),
        "llm_provider": provider,
        "llm_model": model,
    }
