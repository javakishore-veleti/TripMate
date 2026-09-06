from langchain_core.messages import AIMessage

from adapters.agentic.langgraph.agents.utils import complete_text, destination_from_state
from common.dtos import TravelState
from common.log import get_logger

logger = get_logger(__name__)


def hotel_agent(state: TravelState):
    destination = destination_from_state(state)
    logger.info("hotel_agent started destination=%s", destination)
    prompt = f"""
Best hotels for:
{state['user_query']}

Trip Constraints:
{state.get('trip_constraints', {})}

Destination:
{destination}

Live hotel search is temporarily unavailable. Recommend 3 to 5 neighborhoods
or hotel types only. Keep the answer under 220 words and label it as
non-live advice.
"""

    try:
        hotel_results = complete_text(
            "You are an expert travel hotel planner.",
            prompt,
            state,
        )
    except Exception as exc:
        logger.exception("hotel_agent failed: %s", exc)
        hotel_results = (
            "Live hotel search is temporarily unavailable. "
            "Provide general accommodation and neighborhood "
            "guidance based on the destination and clearly "
            "label it as non-live advice."
        )

    logger.info("hotel_agent finished")
    return {
        "hotel_results": hotel_results,
        "messages": [AIMessage(content="Hotel information processed.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
