from langchain_core.messages import AIMessage

from middleware.adapters.agentic.langgraph.llm_text import complete_text, specialist_notes
from middleware.adapters.agentic.langgraph.runtime import brief_failure
from middleware.common.dtos import TravelState
from middleware.common.log import get_logger

logger = get_logger(__name__)


def cost_review(state: TravelState):
    logger.info("cost_review started")
    notes = specialist_notes(state)
    prompt = f"""
Judge whether this trip fits the traveler's budget.

Traveler request:
{state["user_query"]}

Trip notes:
{state.get("trip_constraints", {})}

Air notes:
{notes["flights"]}

Stay notes:
{notes["hotels"]}

Climate notes:
{notes["weather"]}

Cover:
1. Cost buckets
2. Budget risks
3. Ways to save
4. Overall fit

Keep it under 220 words. Label missing live prices as estimates.
"""
    try:
        text = complete_text(
            "You review trip cost for Your Next Travel.",
            prompt,
            state,
            job="reason",
        )
    except Exception as exc:
        logger.exception("cost_review failed: %s", exc)
        text = (
            "Cost review is unavailable right now. Treat air and stay figures "
            "as estimates and keep the draft conservative."
        )
        failure = brief_failure(state, "cost_review", exc)
    else:
        failure = {}
    logger.info("cost_review finished")
    return {
        "budget_results": text,
        "messages": [AIMessage(content="Cost review added.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
        **failure,
    }
