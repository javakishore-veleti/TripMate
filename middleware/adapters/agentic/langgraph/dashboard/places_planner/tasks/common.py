from datetime import date

from middleware.adapters.agentic.langgraph.llm_text import complete_text, json_from_llm
from middleware.adapters.agentic.langgraph.dashboard.places_planner.windows import clean_event, window_for
from middleware.common.default_places import preferences_for_pipeline
from middleware.common.log import get_logger
from middleware.common.popular_events import catalog_prompt_lines, events_near, months_for_horizon
from middleware.common.user_preferences import format_place

logger = get_logger(__name__)

_FOCUS = {
    "week": "Focus on what is happening now through the next seven days — weekends, openings, and dates that land this week.",
    "month": "Focus on this calendar month. Include multi-day festivals that overlap the month.",
    "quarter": "Focus on this quarter — seasonal moments, big festivals, and culture that defines these three months.",
}


def collect_events(state: dict, horizon: str) -> dict:
    prefs, _source = preferences_for_pipeline(state.get("user_preferences"))
    places = prefs["places"]
    radius = prefs["event_radius_miles"]
    anchors = [format_place(place) for place in places]
    _start, _end, window = window_for(horizon)
    today = date.today()
    focus = _FOCUS.get(horizon, _FOCUS["month"])
    months = months_for_horizon(horizon, today)
    known = catalog_prompt_lines(anchors, months, limit=12)
    logger.info("places task horizon=%s places=%s radius=%s", horizon, len(anchors), radius)
    events = []
    try:
        text = complete_text(
            system_prompt=(
                "You are a local travel brief, not a ticket vendor. "
                "Name public festivals, cultural dates, and seasonal moments a traveler could plan around. "
                "Do not invent private addresses. Prefer local neighborhood days people miss, "
                "not only Christmas, Thanksgiving, New Year, or Presidents’ Day. Reply with JSON only."
            ),
            user_prompt=(
                f"Today is {today.isoformat()}.\n"
                f"{focus}\n"
                f"Find popular public events {window} within about {radius} miles of these places:\n"
                + "\n".join(f"- {anchor}" for anchor in anchors)
                + (f"\n\n{known}\n" if known else "\n")
                + "\nReturn JSON only:\n"
                '{"events":[{"name":"","kind":"festival|culture|season|community",'
                '"city":"","region":"","country":"","when":"","miles_from":0,'
                '"near":"one of the listed places","blurb":"one short sentence"}]}\n'
                "Give 4 to 8 real events. Stay inside the radius. "
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
        for item in raw_events:
            if not isinstance(item, dict):
                continue
            cleaned = clean_event(item, anchors[0] if anchors else "")
            if cleaned and (cleaned["miles_from"] <= radius or cleaned["miles_from"] == 0):
                events.append(cleaned)
            if len(events) >= 8:
                break
    except Exception as exc:
        logger.warning("places planner fallback: %s", exc)
    if len(events) < 4:
        known_names = {item["name"] for item in events}
        for spark in events_near(anchors, months, 8):
            if spark["name"] in known_names:
                continue
            events.append(spark)
            if len(events) >= 8:
                break
    return {
        "horizon": horizon,
        "window": window,
        "radius_miles": radius,
        "places": anchors,
        "events": events[:8],
    }
