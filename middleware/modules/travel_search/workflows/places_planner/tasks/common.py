from datetime import date

from middleware.adapters.agentic.langgraph.llm_text import complete_text, json_from_llm
from middleware.modules.travel_search.workflows.places_planner.windows import clean_event, window_for
from middleware.common.log import get_logger
from middleware.common.user_preferences import format_place, normalize_preferences

logger = get_logger(__name__)

_FOCUS = {
    "week": "Focus on what is happening now through the next seven days — weekends, openings, and dates that land this week.",
    "month": "Focus on this calendar month. Include multi-day festivals that overlap the month.",
    "quarter": "Focus on this quarter — seasonal moments, big festivals, and culture that defines these three months.",
}


def collect_events(state: dict, horizon: str) -> dict:
    prefs = normalize_preferences(state.get("user_preferences"))
    places = prefs["places"]
    radius = prefs["event_radius_miles"]
    anchors = [format_place(place) for place in places]
    _start, _end, window = window_for(horizon)
    today = date.today()
    focus = _FOCUS.get(horizon, _FOCUS["month"])
    logger.info("places task horizon=%s places=%s radius=%s", horizon, len(anchors), radius)
    text = complete_text(
        system_prompt=(
            "You are a local travel brief, not a ticket vendor. "
            "Name public festivals, cultural dates, and seasonal moments a traveler could plan around. "
            "Do not invent private addresses. Prefer widely known events. Reply with JSON only."
        ),
        user_prompt=(
            f"Today is {today.isoformat()}.\n"
            f"{focus}\n"
            f"Find popular public events {window} within about {radius} miles of these places:\n"
            + "\n".join(f"- {anchor}" for anchor in anchors)
            + "\n\nReturn JSON only:\n"
            '{"events":[{"name":"","kind":"festival|culture|season|community",'
            '"city":"","region":"","country":"","when":"","miles_from":0,'
            '"near":"one of the listed places","blurb":"one short sentence"}]}\n'
            "Give 4 to 8 real, well-known events. Stay inside the radius. "
            "If something is famous but farther, skip it. miles_from is an estimate from the nearest listed place."
        ),
        state=state,
        max_tokens=1200,
        job="reason",
    )
    parsed = json_from_llm(text)
    raw_events = parsed.get("events") if isinstance(parsed, dict) else parsed
    if not isinstance(raw_events, list):
        raw_events = []
    events = []
    for item in raw_events:
        if not isinstance(item, dict):
            continue
        cleaned = clean_event(item, anchors[0] if anchors else "")
        if cleaned and cleaned["miles_from"] <= radius:
            events.append(cleaned)
    return {
        "horizon": horizon,
        "window": window,
        "radius_miles": radius,
        "places": anchors,
        "events": events[:8],
    }
