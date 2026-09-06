from langgraph.graph import END

from middleware.adapters.agentic.langgraph.specialists.ids import (
    AIR_RESEARCH,
    CLIMATE_BRIEF,
    COORDINATOR,
    COST_REVIEW,
    REQUEST_DECLINED,
    SPECIALIST_ORDER,
    STAY_RESEARCH,
    TRIP_DRAFT,
)
from middleware.common.dtos import TravelState

ROUTE_MAP = {
    REQUEST_DECLINED: REQUEST_DECLINED,
    COORDINATOR: COORDINATOR,
    AIR_RESEARCH: AIR_RESEARCH,
    STAY_RESEARCH: STAY_RESEARCH,
    CLIMATE_BRIEF: CLIMATE_BRIEF,
    COST_REVIEW: COST_REVIEW,
    TRIP_DRAFT: TRIP_DRAFT,
    END: END,
}


def _next_specialist(state: TravelState, current: str | None) -> str:
    selected = state.get("selected_specialists") or []
    start_after = -1
    if current is not None:
        try:
            start_after = SPECIALIST_ORDER.index(current)
        except ValueError:
            start_after = -1
    for name in SPECIALIST_ORDER[start_after + 1 :]:
        if name in selected:
            return name
    return TRIP_DRAFT


def route_after_intake(state: TravelState) -> str:
    if state.get("request_accepted") is False:
        return REQUEST_DECLINED
    return COORDINATOR


def route_from_coordinator(state: TravelState) -> str:
    return _next_specialist(state, None)


def route_after_specialist(current: str):
    def _route(state: TravelState) -> str:
        return _next_specialist(state, current)

    return _route
