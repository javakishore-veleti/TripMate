from middleware.adapters.agentic.langgraph.journal.happenings.roles import complete_role
from middleware.adapters.agentic.langgraph.llm_text import json_from_llm
from middleware.common.log import get_logger

logger = get_logger(__name__)


def classify_traveler(state: dict) -> dict:
    packs = state.get("skill_names") or []
    places = state.get("places") or []
    pack_line = ", ".join(packs) if packs else "account travel style only"
    try:
        raw = complete_role(
            "classify",
            "Classify how this traveler wants to spend nearby time. Return JSON only.",
            (
                f"Places: {', '.join(places) or 'none'}\n"
                f"Preference packs: {pack_line}\n"
                "Return JSON only:\n"
                '{"lens":"festivals|food|outdoors|culture|family|mix",'
                '"note":"one short sentence about what to look for this month"}'
            ),
            state,
        )
        parsed = json_from_llm(raw)
        lens = str(parsed.get("lens") or "mix").strip().lower()
        if lens not in {"festivals", "food", "outdoors", "culture", "family", "mix"}:
            lens = "mix"
        note = str(parsed.get("note") or "").strip()
    except Exception as exc:
        logger.warning("journal classify fallback: %s", exc)
        lens = "mix"
        note = "Look for public festivals, food, and seasonal moments near your places."
    logger.info("journal classify lens=%s", lens)
    return {"lens": lens, "classify_note": note}
