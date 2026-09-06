from middleware.adapters.agentic.langgraph.llm_text import complete_text, json_from_llm
from middleware.adapters.agentic.langgraph.specialists.ids import (
    AIR_RESEARCH,
    CLIMATE_BRIEF,
    COORDINATOR,
    COST_REVIEW,
    INTAKE,
    PLAN_ASSEMBLE,
    REQUEST_DECLINED,
    STAY_RESEARCH,
    TRAVELER_REVIEW,
    TRIP_DRAFT,
)
from middleware.common.dtos import TravelState
from middleware.common.log import get_logger

logger = get_logger(__name__)

FLAVOR_KEYS = (
    "watching",
    "started",
    "opening",
    INTAKE,
    COORDINATOR,
    AIR_RESEARCH,
    STAY_RESEARCH,
    CLIMATE_BRIEF,
    COST_REVIEW,
    TRIP_DRAFT,
    TRAVELER_REVIEW,
    PLAN_ASSEMBLE,
    REQUEST_DECLINED,
    "finished",
)

_FALLBACK = {
    "watching": "The desk just woke up for this trip.",
    "started": "A fresh map is unfolding.",
    "opening": "The specialists are taking their seats.",
    INTAKE: "Every detail in the ask gets a look.",
    COORDINATOR: "The right research is lining up.",
    AIR_RESEARCH: "Seats and skies are coming into view.",
    STAY_RESEARCH: "Nights and neighborhoods are taking shape.",
    CLIMATE_BRIEF: "The season is whispering what to pack.",
    COST_REVIEW: "The numbers are finding their fit.",
    TRIP_DRAFT: "Days are stacking into a story.",
    TRAVELER_REVIEW: "Your call comes next.",
    PLAN_ASSEMBLE: "The last pieces are clicking in.",
    REQUEST_DECLINED: "This ask needs a clearer turn.",
    "finished": "This pass is on the table.",
}


def _clip_flavor(text: str) -> str:
    cleaned = " ".join(str(text or "").replace('"', "").split()).strip()
    if cleaned.endswith(".."):
        cleaned = cleaned.rstrip(".") + "."
    if cleaned and cleaned[-1] not in ".!?":
        cleaned = f"{cleaned}."
    if len(cleaned) <= 72:
        return cleaned
    cut = cleaned[:71]
    at = cut.rfind(" ")
    return f"{cut[: at if at > 24 else 71].rstrip('.,;:')}."


def flavor_lines(ask: str, state: TravelState | None = None) -> dict[str, str]:
    lines = dict(_FALLBACK)
    prompt = f"""
Write one short lively sentence for each pipeline step. Tie it to this trip.
Max 12 words. No quotes. No lists. No extra keys.

Return JSON only:
{{
  "watching": "",
  "started": "",
  "opening": "",
  "{INTAKE}": "",
  "{COORDINATOR}": "",
  "{AIR_RESEARCH}": "",
  "{STAY_RESEARCH}": "",
  "{CLIMATE_BRIEF}": "",
  "{COST_REVIEW}": "",
  "{TRIP_DRAFT}": "",
  "{TRAVELER_REVIEW}": "",
  "{PLAN_ASSEMBLE}": "",
  "{REQUEST_DECLINED}": "",
  "finished": ""
}}

Trip ask:
{ask}
"""
    try:
        raw = complete_text(
            "You write tiny travel-desk asides. JSON only. One short sentence per key.",
            prompt,
            state,
            max_tokens=280,
            job="classify",
        )
        parsed = json_from_llm(raw)
        for key in FLAVOR_KEYS:
            value = _clip_flavor(str(parsed.get(key) or ""))
            if value:
                lines[key] = value
    except Exception as exc:
        logger.warning("pipeline flavor fallback used: %s", exc)
    return lines


def with_flavor(label: str, flavor: str) -> str:
    extra = " ".join(str(flavor or "").split()).strip()
    if not extra:
        return label
    return f"{label} {extra}"
