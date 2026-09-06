from langchain_core.messages import AIMessage

from adapters.agentic.langgraph.agents.utils import complete_text, destination_from_state
from common.dtos import TravelState
from common.log import get_logger

logger = get_logger(__name__)

FLIGHT_AGENT_PROMPT = """
You are a travel flight expert.

User Query:
{query}

Trip Constraints:
{trip_constraints}

Airport Information:
{airport_data}

Airline Information:
{airline_data}

Generate:
1. Likely departure airport
2. Likely arrival airport
3. Airlines serving this route
4. Typical flight duration
5. Estimated airfare range
6. Peak season pricing warning
7. Booking advice

Return concise travel guidance in under 220 words.
"""


def flight_agent(state: TravelState):
    query = state["user_query"]
    destination = destination_from_state(state)
    logger.info("flight_agent started destination=%s", destination)

    try:
        prompt = FLIGHT_AGENT_PROMPT.format(
            query=query,
            trip_constraints=state.get("trip_constraints", {}),
            airport_data=(
                f"Live airport listing is unavailable. Infer likely airports "
                f"for {destination or query} from the request."
            ),
            airline_data=(
                "Live airline listing is unavailable. Infer typical carriers "
                "for this route and label estimates as approximate."
            ),
        )
        flight_data = complete_text(
            "You are an expert travel flight planner.",
            prompt,
            state,
        )
    except Exception as exc:
        logger.exception("flight_agent failed: %s", exc)
        flight_data = f"Flight information unavailable: {exc}"

    logger.info("flight_agent finished")
    return {
        "flight_results": flight_data,
        "messages": [AIMessage(content="Flight recommendations generated")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
