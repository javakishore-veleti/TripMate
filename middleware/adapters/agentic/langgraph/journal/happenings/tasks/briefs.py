from middleware.adapters.agentic.langgraph.journal.happenings.roles import complete_role
from middleware.common.log import get_logger

logger = get_logger(__name__)


def _event_lines(state: dict) -> str:
    lines = []
    for event in state.get("events") or []:
        lines.append(
            f"- {event.get('name')} ({event.get('when') or event.get('day') or 'this month'}) "
            f"near {event.get('near')}"
        )
    return "\n".join(lines) or "- no events listed"


def pack_brief(state: dict) -> dict:
    logger.info("journal pack brief")
    try:
        text = complete_role(
            "deep",
            "Think through what this traveler should pack for nearby events this month.",
            (
                f"Places: {', '.join(state.get('places') or [])}\n"
                f"Lens: {state.get('lens')}\n"
                f"Events:\n{_event_lines(state)}\n\n"
                "Write a short packing brief (under 120 words): weather layers, "
                "festival vs dinner clothes, and one thing not to forget."
            ),
            state,
        )
    except Exception as exc:
        logger.warning("journal pack fallback: %s", exc)
        text = "Pack a light layer, comfortable shoes, and a small bag for day festivals."
    return {"pack": text.strip()}


def food_brief(state: dict) -> dict:
    logger.info("journal food brief")
    try:
        text = complete_role(
            "deep",
            "Think through the food worth looking for near these events.",
            (
                f"Places: {', '.join(state.get('places') or [])}\n"
                f"Events:\n{_event_lines(state)}\n\n"
                "Write a short food brief (under 120 words): seasonal plates, "
                "festival snacks, and one local thing to try."
            ),
            state,
        )
    except Exception as exc:
        logger.warning("journal food fallback: %s", exc)
        text = "Look for seasonal festival food and one local plate you cannot get at home."
    return {"food": text.strip()}


def ideas_brief(state: dict) -> dict:
    logger.info("journal ideas brief")
    try:
        text = complete_role(
            "deep",
            "Think through the kinds of short trips that fit these happenings.",
            (
                f"Places: {', '.join(state.get('places') or [])}\n"
                f"Preference packs: {', '.join(state.get('skill_names') or []) or 'none'}\n"
                f"Events:\n{_event_lines(state)}\n\n"
                "Suggest 3 short travel-plan shapes (weekend, food crawl, festival stay). "
                "Under 140 words. Do not invent ticket prices."
            ),
            state,
        )
    except Exception as exc:
        logger.warning("journal ideas fallback: %s", exc)
        text = "A weekend around one festival, a food-led day trip, or a two-night stay near the biggest event."
    return {"ideas": text.strip()}
