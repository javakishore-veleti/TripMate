from langgraph.graph import END

from common.dtos import TravelState

AGENT_ORDER = [
    "flight_agent",
    "hotel_agent",
    "weather_agent",
    "budget_agent",
    "itinerary_agent",
]

ROUTE_MAP = {
    "guardrail_blocked": "guardrail_blocked",
    "flight_agent": "flight_agent",
    "hotel_agent": "hotel_agent",
    "weather_agent": "weather_agent",
    "budget_agent": "budget_agent",
    "itinerary_agent": "itinerary_agent",
    END: END,
}


def _next_agent(state: TravelState, current: str | None) -> str:
    selected = state.get("selected_agents") or []
    start_after = -1
    if current is not None:
        try:
            start_after = AGENT_ORDER.index(current)
        except ValueError:
            start_after = -1
    for name in AGENT_ORDER[start_after + 1 :]:
        if name in selected:
            return name
    return "itinerary_agent"


def route_from_supervisor(state: TravelState) -> str:
    if state.get("guardrail_allowed") is False:
        return "guardrail_blocked"
    return _next_agent(state, None)


def route_after_agent(current: str):
    def _route(state: TravelState) -> str:
        return _next_agent(state, current)

    return _route
