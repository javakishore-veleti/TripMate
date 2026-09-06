from langchain_core.messages import AIMessage

from adapters.agentic.langgraph.agents.utils import complete_text, specialist_notes
from common.dtos import TravelState
from common.log import get_logger

logger = get_logger(__name__)


def budget_agent(state: TravelState):
    logger.info("budget_agent started")
    notes = specialist_notes(state)
    prompt = f"""
Analyze whether this trip is realistic for the user's budget.

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

Return:
1. Estimated cost categories
2. Budget risk areas
3. Money-saving suggestions
4. Overall feasibility

Keep the answer under 220 words. If exact live prices are unavailable, label estimates as approximate.
"""

    try:
        budget_results = complete_text(
            "You are a practical travel budget analyst.",
            prompt,
            state,
        )
    except Exception as exc:
        logger.exception("budget_agent failed: %s", exc)
        budget_results = (
            "Budget analysis is temporarily unavailable because the model "
            "rate limit was reached. Treat flight and hotel figures as "
            "approximate and keep the itinerary conservative."
        )
    logger.info("budget_agent finished")

    return {
        "budget_results": budget_results,
        "messages": [AIMessage(content="Budget assessment generated.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
