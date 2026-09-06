from langchain_core.messages import AIMessage

from adapters.agentic.langgraph.agents.utils import (
    JSON_MAX_TOKENS,
    complete_text,
    empty_constraints,
    json_from_llm,
)
from adapters.agentic.langgraph.routes import AGENT_ORDER
from common.dtos import TravelState
from common.log import get_logger, preview
from common.user_preferences import apply_preferences_to_constraints

logger = get_logger(__name__)

KNOWN_AGENTS = set(AGENT_ORDER)


# =========================
# Supervisor Agent + Input Guardrail
# =========================
def supervisor_agent(state: TravelState):
    query = state["user_query"]
    llm_calls = state.get("llm_calls", 0)
    logger.info("supervisor started query=%s", preview(query))

    guardrail_prompt = f"""
    Determine whether the following request belongs to travel planning or travel
    information. Valid requests can include destinations, flights, hotels, weather,
    budgets, visas, transportation, sightseeing, food, packing, or itineraries.

    Block clearly unrelated requests and requests asking for harmful or illegal
    instructions. Do not block a valid travel request merely because some details
    are missing.

    Return strict JSON only:
    {{
    "allowed": true,
    "reason": ""
    }}

    User request:
    {query}
    """

    # Fail open on parser/model errors so a temporary JSON-format issue does not
    # break the original travel-planning behavior.
    try:
        guardrail_raw = complete_text(
            "You are the input guardrail for a travel-planning "
            "application. Return strict JSON only.",
            guardrail_prompt,
            state,
            max_tokens=JSON_MAX_TOKENS,
        )
        guardrail_result = json_from_llm(guardrail_raw)
        allowed = bool(guardrail_result.get("allowed", True))
        guardrail_reason = str(guardrail_result.get("reason", "")).strip()
        llm_calls += 1
    except Exception as exc:
        logger.warning("guardrail fallback used: %s", exc)
        allowed = True
        guardrail_reason = "Guardrail validation fallback allowed the request."

    if not allowed:
        reason = guardrail_reason or (
            "Your Next Travel can only help with travel-planning requests. "
            "Please ask about a destination, flight, hotel, weather, budget, "
            "or itinerary."
        )
        logger.info("guardrail blocked reason=%s", preview(reason))
        return {
            "guardrail_allowed": False,
            "guardrail_reason": reason,
            "selected_agents": [],
            "trip_constraints": empty_constraints(),
            "supervisor_reasoning": reason,
            "final_response": reason,
            "messages": [AIMessage(content=f"Guardrail blocked request: {reason}")],
            "llm_calls": llm_calls,
        }

    supervisor_prompt = f"""
You are the supervisor of a multi-agent travel-planning system.
Choose only the specialist agents needed for the request.
When the user omits origin, budget, or travel style, take those from the traveler profile.

Available agents:
- flight_agent: flights, airports, airlines, routes, airfare, or booking advice
- hotel_agent: hotels, accommodation, neighborhoods, or places to stay
- weather_agent: weather, climate, season, forecast, or packing advice
- budget_agent: cost, affordability, price limits, or budget feasibility
- itinerary_agent: creates the integrated travel plan and must always be included

Return strict JSON only using this schema:
{{
  "selected_agents": ["flight_agent", "hotel_agent", "weather_agent", "budget_agent", "itinerary_agent"],
  "trip_constraints": {{
    "destination": "",
    "origin": "",
    "duration": "",
    "budget": "",
    "travel_style": "",
    "special_preferences": []
  }},
  "reasoning": ""
}}

User request:
{query}
"""

    try:
        supervisor_raw = complete_text(
            "You route work to travel specialist agents. Return strict JSON only.",
            supervisor_prompt,
            state,
            max_tokens=JSON_MAX_TOKENS,
        )
        parsed = json_from_llm(supervisor_raw)
        requested_agents = parsed.get("selected_agents", [])
        selected_agents = [
            name for name in AGENT_ORDER
            if name in requested_agents and name in KNOWN_AGENTS
        ]

        # The itinerary agent integrates whichever specialist results were selected.
        if "itinerary_agent" not in selected_agents:
            selected_agents.append("itinerary_agent")

        constraints = empty_constraints()
        parsed_constraints = parsed.get("trip_constraints", {})
        if isinstance(parsed_constraints, dict):
            constraints.update(parsed_constraints)
        apply_preferences_to_constraints(constraints, state.get("user_preferences"))

        reasoning = str(parsed.get("reasoning", "")).strip()
        llm_calls += 1
    except Exception as exc:
        logger.warning("supervisor fallback used: %s", exc)
        # Original workflow behavior is preserved as the fallback.
        selected_agents = AGENT_ORDER.copy()
        constraints = apply_preferences_to_constraints(
            empty_constraints(),
            state.get("user_preferences"),
        )
        reasoning = (
            "Supervisor parsing failed, so the original full travel workflow "
            "was selected as a safe fallback."
        )

    logger.info("supervisor selected agents=%s", selected_agents)
    return {
        "guardrail_allowed": True,
        "guardrail_reason": guardrail_reason,
        "selected_agents": selected_agents,
        "trip_constraints": constraints,
        "supervisor_reasoning": reasoning,
        "messages": [AIMessage(content="Supervisor created the agent plan.")],
        "llm_calls": llm_calls,
    }