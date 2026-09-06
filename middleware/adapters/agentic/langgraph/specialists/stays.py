from langchain_core.messages import AIMessage

from middleware.adapters.agentic.langgraph.llm_text import complete_text, destination_from_state
from middleware.adapters.agentic.langgraph.runtime import brief_failure
from middleware.common.dtos import TravelState
from middleware.common.log import get_logger

logger = get_logger(__name__)


def stay_research(state: TravelState):
    destination = destination_from_state(state)
    logger.info("stay_research started destination=%s", destination)
    prompt = f"""
Suggest where to stay. This is neighborhood and stay-type advice, not a live booking search.

Traveler request:
{state["user_query"]}

Trip notes:
{state.get("trip_constraints", {})}

Destination:
{destination}

Recommend 3 to 5 neighborhoods or stay types. Keep it under 220 words.
"""
    try:
        text = complete_text(
            "You research stays for Your Next Travel. Give non-live neighborhood advice.",
            prompt,
            state,
            job="reason",
        )
    except Exception as exc:
        logger.exception("stay_research failed: %s", exc)
        text = (
            "Stay search is unavailable right now. Use the destination and "
            "travel style to pick a neighborhood, and treat this as non-live advice."
        )
        failure = brief_failure(state, "stay_research", exc)
    else:
        failure = {}
    logger.info("stay_research finished")
    return {
        "hotel_results": text,
        "messages": [AIMessage(content="Stay research added.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
        **failure,
    }
