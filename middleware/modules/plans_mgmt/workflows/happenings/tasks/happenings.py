from calendar import monthrange
from datetime import date

from middleware.modules.travel_search.workflows.places_planner.windows import clean_event
from middleware.modules.plans_mgmt.workflows.happenings.roles import complete_role
from middleware.adapters.agentic.langgraph.llm_text import json_from_llm
from middleware.common.log import get_logger

logger = get_logger(__name__)


def collect_month_happenings(state: dict) -> dict:
    today = date.today()
    year = int(state.get("year") or today.year)
    month = int(state.get("month") or today.month)
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    window = f"{start.strftime('%B %Y')} ({start.isoformat()} to {end.isoformat()})"
    expand = bool(state.get("expand"))
    limit = 12 if expand else 5
    places = state.get("places") or []
    radius = int(state.get("radius_miles") or 200)
    packs = state.get("skill_names") or []
    lens = state.get("lens") or "mix"
    logger.info("journal happenings month=%s expand=%s limit=%s", window, expand, limit)
    prompt = f"""
Today is {today.isoformat()}.
List well-known public events in {window} within about {radius} miles of:
{chr(10).join(f'- {place}' for place in places) or '- (no places saved)'}

Traveler lens: {lens}
Preference packs: {', '.join(packs) or 'none selected'}

Name real festivals, parades, food weeks, film/music events, and seasonal moments
a traveler could plan around — SXSW, Jazz Fest, Pride, ACL, Sundance, Lunar New Year,
Oktoberfest, and local equivalents near these places. Do not invent street addresses.
Stay inside the radius. If something famous is farther, skip it.

Return JSON only:
{{
  "events": [
    {{
      "name": "",
      "kind": "festival|culture|season|community",
      "city": "",
      "region": "",
      "country": "",
      "when": "human date",
      "day": "YYYY-MM-DD if known, else empty",
      "miles_from": 0,
      "near": "one of the listed places",
      "blurb": "one short sentence"
    }}
  ]
}}

Give the top {limit} events, strongest first.
"""
    events = []
    try:
        raw = complete_role(
            "reason",
            "You reason about what is happening near the traveler this month. Return JSON only.",
            prompt,
            state,
        )
        parsed = json_from_llm(raw)
        raw_events = parsed.get("events") if isinstance(parsed, dict) else parsed
        if not isinstance(raw_events, list):
            raw_events = []
        for item in raw_events:
            if not isinstance(item, dict):
                continue
            cleaned = clean_event(item, places[0] if places else "")
            if cleaned and cleaned["miles_from"] <= radius:
                events.append(cleaned)
            if len(events) >= limit:
                break
    except Exception as exc:
        logger.warning("journal happenings fallback: %s", exc)
    return {
        "window": window,
        "events": events,
        "year": year,
        "month": month,
    }
