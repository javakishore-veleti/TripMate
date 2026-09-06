from langchain_core.messages import AIMessage

from middleware.adapters.agentic.langgraph.llm_text import complete_text, destination_from_state
from middleware.adapters.agentic.langgraph.runtime import brief_failure
from middleware.common.dtos import TravelState
from middleware.common.log import get_logger

logger = get_logger(__name__)


def climate_brief(state: TravelState):
    city = destination_from_state(state)
    logger.info("climate_brief started city=%s", city)
    prompt = f"""
Give practical weather and packing guidance for this trip.

Place:
{city}

Traveler request:
{state["user_query"]}

Trip notes:
{state.get("trip_constraints") or {}}

Live forecast tools are not connected. Give seasonal guidance in under 160 words
and label it as non-live advice.

Use:
Season now:
<guidance>

What to pack:
<guidance>
"""
    try:
        text = complete_text(
            "You write climate briefs for Your Next Travel.",
            prompt,
            state,
            job="reason",
        )
    except Exception as exc:
        logger.exception("climate_brief failed: %s", exc)
        text = (
            f"A live forecast for {city} is unavailable. Use seasonal packing "
            "and check the weather before departure."
        )
        failure = brief_failure(state, "climate_brief", exc)
    else:
        failure = {}
    logger.info("climate_brief finished")
    return {
        "weather_results": text,
        "messages": [AIMessage(content="Climate brief added.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
        **failure,
    }
