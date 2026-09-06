from langchain_core.messages import AIMessage

from middleware.adapters.agentic.langgraph.llm_text import complete_text, destination_from_state
from middleware.common.dtos import TravelState
from middleware.common.log import get_logger

logger = get_logger(__name__)


def air_research(state: TravelState):
    query = state["user_query"]
    destination = destination_from_state(state)
    logger.info("air_research started destination=%s", destination)
    prompt = f"""
Sketch practical air options for this trip. These are planning estimates, not tickets.

Traveler request:
{query}

Trip notes:
{state.get("trip_constraints", {})}

Destination:
{destination}

Cover:
1. Likely departure airport
2. Likely arrival airport
3. Typical carriers on the route
4. Typical flight time
5. Approximate fare range
6. Busy-season price warning
7. Booking tips

Keep it under 220 words and label figures as estimates.
"""
    try:
        text = complete_text(
            "You research air options for Your Next Travel. Give planning estimates only.",
            prompt,
            state,
            job="reason",
        )
    except Exception as exc:
        logger.exception("air_research failed: %s", exc)
        text = f"Air options are unavailable right now: {exc}"
    logger.info("air_research finished")
    return {
        "flight_results": text,
        "messages": [AIMessage(content="Air research added.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
