from middleware.adapters.agentic.langgraph.journal.happenings.roles import complete_role
from middleware.adapters.agentic.langgraph.llm_text import json_from_llm
from middleware.common.log import get_logger

logger = get_logger(__name__)

_FALLBACK_NOTE = "Go find a spark near your cities."
_INSTRUCTION_BITS = (
    "one short sentence",
    "what to look for",
    "return json",
    "json only",
    "this month}",
    "look for this month",
)


def lively_note(raw) -> str:
    note = " ".join(str(raw or "").split()).strip().strip('"')
    lowered = note.lower()
    if not note or any(bit in lowered for bit in _INSTRUCTION_BITS):
        return _FALLBACK_NOTE
    words = note.split()
    if len(words) > 12:
        note = " ".join(words[:12]).rstrip(".,;:") + "."
    return note


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
                '"note":"Go taste the night markets this month."}\n'
                "note: eight words max. Make them want to go. No instructions."
            ),
            state,
        )
        parsed = json_from_llm(raw)
        lens = str(parsed.get("lens") or "mix").strip().lower()
        if lens not in {"festivals", "food", "outdoors", "culture", "family", "mix"}:
            lens = "mix"
        note = lively_note(parsed.get("note"))
    except Exception as exc:
        logger.warning("journal classify fallback: %s", exc)
        lens = "mix"
        note = _FALLBACK_NOTE
    logger.info("journal classify lens=%s", lens)
    return {"lens": lens, "classify_note": note}
