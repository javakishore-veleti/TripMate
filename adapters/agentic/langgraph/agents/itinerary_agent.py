from langchain_core.messages import AIMessage

from adapters.agentic.langgraph.agents.utils import (
    PLAN_MAX_TOKENS,
    complete_text,
    specialist_notes,
)
from common.dtos import TravelState
from common.log import get_logger

logger = get_logger(__name__)


def itinerary_agent(state: TravelState):
    logger.info("itinerary_agent started")
    notes = specialist_notes(state)
    prompt = f"""
Create a complete travel itinerary.

User Query:
{state['user_query']}

Trip Constraints:
{state.get('trip_constraints', {})}

Flight Results:
{notes['flights']}

Hotel Results:
{notes['hotels']}

Weather Results:
{notes['weather']}

Budget Results:
{notes['budget']}

Make the itinerary practical, budget-aware, and easy to follow.
Create a clear draft that is ready for human review.
Keep it under 450 words.
"""

    try:
        itinerary = complete_text(
            "You are an expert travel planner.",
            prompt,
            state,
            max_tokens=PLAN_MAX_TOKENS,
        )
    except Exception as exc:
        logger.exception("itinerary_agent failed: %s", exc)
        itinerary = (
            "A full draft itinerary could not be generated because the model "
            "rate limit was reached. Use the specialist notes above as a "
            "starting point and ask the traveler to retry in a minute."
        )
    logger.info("itinerary_agent finished")
    approval_request = (
        "Please review the generated draft itinerary. Approve it to create the "
        "final polished plan, or provide feedback for revision."
    )

    return {
        "itinerary": itinerary,
        "approval_request": approval_request,
        "messages": [AIMessage(content="Draft itinerary created for human review.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
