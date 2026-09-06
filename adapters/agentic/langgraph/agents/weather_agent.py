from langchain_core.messages import AIMessage

from adapters.agentic.langgraph.agents.utils import complete_text, destination_from_state
from common.dtos import TravelState
from common.log import get_logger

logger = get_logger(__name__)


def weather_agent(state: TravelState):
    city = destination_from_state(state)
    logger.info("weather_agent started city=%s", city)

    constraints = state.get("trip_constraints") or {}
    try:
        weather_results = complete_text(
            "You are a travel weather advisor.",
            f"""
Give practical weather guidance for this trip.

City / destination:
{city}

User Query:
{state['user_query']}

Trip Constraints:
{constraints}

Live weather and forecast tools are temporarily unavailable. Give brief
seasonal guidance and packing notes in under 160 words. Label this as
non-live advice.

Format:
Current Weather:
<guidance>

Forecast:
<guidance>
""",
            state,
        )
    except Exception as exc:
        logger.exception("weather_agent failed: %s", exc)
        weather_results = (
            f"Live weather information for {city} "
            "is temporarily unavailable. Give general "
            "seasonal guidance and advise the traveler "
            "to verify the forecast before departure."
        )

    logger.info("weather_agent finished")
    return {
        "weather_results": weather_results,
        "messages": [AIMessage(content="Weather information processed.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
