from langchain_core.messages import AIMessage

from middleware.adapters.agentic.langgraph.llm_text import PLAN_MAX_TOKENS, complete_text, specialist_notes
from middleware.common.dtos import TravelState
from middleware.common.log import get_logger

logger = get_logger(__name__)


def trip_draft(state: TravelState):
    logger.info("trip_draft started")
    notes = specialist_notes(state)
    prompt = f"""
Write a practical trip draft the traveler can review.

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

Cost notes:
{notes["budget"]}

Keep it easy to follow and under 450 words.
"""
    try:
        itinerary = complete_text(
            "You draft day plans for Your Next Travel.",
            prompt,
            state,
            max_tokens=PLAN_MAX_TOKENS,
            job="deep",
        )
    except Exception as exc:
        logger.exception("trip_draft failed: %s", exc)
        itinerary = (
            "A full draft could not be written just now. Use the research notes "
            "above and ask the traveler to retry in a minute."
        )
    logger.info("trip_draft finished")
    return {
        "itinerary": itinerary,
        "approval_request": (
            "Review this draft. Approve it to polish the final plan, or send "
            "notes for a revision."
        ),
        "messages": [AIMessage(content="Trip draft is ready for review.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
