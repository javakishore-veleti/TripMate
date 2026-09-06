from langchain_core.messages import AIMessage

from middleware.adapters.agentic.langgraph.llm_text import (
    JSON_MAX_TOKENS,
    complete_text,
    empty_constraints,
    json_from_llm,
)
from middleware.modules.plans_mgmt.tasks.specialists.ids import (
    AIR_RESEARCH,
    CLIMATE_BRIEF,
    COST_REVIEW,
    SPECIALIST_ORDER,
    STAY_RESEARCH,
    TRIP_DRAFT,
)
from middleware.common.dtos import TravelState
from middleware.common.log import get_logger, preview
from middleware.common.user_preferences import apply_preferences_to_constraints

logger = get_logger(__name__)


def coordinator(state: TravelState):
    query = state["user_query"]
    llm_calls = state.get("llm_calls", 0)
    logger.info("coordinator started query=%s", preview(query))
    prompt = f"""
You coordinate a Your Next Travel draft.
Pick only the research modules this request needs.
If origin, budget, or travel style are missing, use the traveler profile.

Modules:
- {AIR_RESEARCH}: flights, airports, airlines, routes, or fare ranges
- {STAY_RESEARCH}: hotels, neighborhoods, or places to stay
- {CLIMATE_BRIEF}: weather, season, forecast, or packing
- {COST_REVIEW}: budget fit, cost risk, or savings
- {TRIP_DRAFT}: always include; it writes the day-by-day draft

Return JSON only:
{{
  "selected_specialists": ["{AIR_RESEARCH}", "{STAY_RESEARCH}", "{CLIMATE_BRIEF}", "{COST_REVIEW}", "{TRIP_DRAFT}"],
  "trip_constraints": {{
    "destination": "",
    "origin": "",
    "duration": "",
    "budget": "",
    "travel_style": "",
    "special_preferences": []
  }},
  "notes": ""
}}

Traveler request:
{query}
"""
    try:
        raw = complete_text(
            "You choose Your Next Travel research modules. Return JSON only.",
            prompt,
            state,
            max_tokens=JSON_MAX_TOKENS,
            job="classify",
        )
        parsed = json_from_llm(raw)
        requested = parsed.get("selected_specialists") or parsed.get("selected_agents") or []
        selected = [name for name in SPECIALIST_ORDER if name in requested]
        if TRIP_DRAFT not in selected:
            selected.append(TRIP_DRAFT)
        constraints = empty_constraints()
        parsed_constraints = parsed.get("trip_constraints", {})
        if isinstance(parsed_constraints, dict):
            constraints.update(parsed_constraints)
        apply_preferences_to_constraints(constraints, state.get("user_preferences"))
        notes = str(parsed.get("notes") or parsed.get("reasoning") or "").strip()
        llm_calls += 1
    except Exception as exc:
        logger.warning("coordinator fallback used: %s", exc)
        selected = SPECIALIST_ORDER.copy()
        constraints = apply_preferences_to_constraints(
            empty_constraints(),
            state.get("user_preferences"),
        )
        notes = "Coordinator could not parse the model reply, so the full trip workflow runs."

    logger.info("coordinator selected=%s", selected)
    return {
        "request_accepted": True,
        "request_note": state.get("request_note", ""),
        "selected_specialists": selected,
        "trip_constraints": constraints,
        "coordinator_notes": notes,
        "messages": [AIMessage(content="Trip research plan is ready.")],
        "llm_calls": llm_calls,
    }
