from langchain_core.messages import AIMessage

from middleware.adapters.agentic.langgraph.llm_text import PLAN_MAX_TOKENS, complete_text, specialist_notes
from middleware.adapters.agentic.langgraph.runtime import brief_failure
from middleware.common.dtos import TravelState
from middleware.common.log import get_logger

logger = get_logger(__name__)


def plan_assemble(state: TravelState):
    logger.info("plan_assemble started approved=%s", state.get("approved", False))
    if state.get("approved", False):
        review_instruction = (
            "The traveler approved the draft. Keep the decisions and polish the writing."
        )
    else:
        review_instruction = (
            "The traveler asked for a revision. Apply these notes:\n"
            f"{state.get('traveler_feedback') or state.get('human_feedback') or 'Improve the draft.'}"
        )
    notes = specialist_notes(state)
    prompt = f"""
Write the traveler-facing trip plan.

Review:
{review_instruction}

Original request:
{state["user_query"]}

Trip notes:
{state.get("trip_constraints", {})}

Air:
{notes["flights"]}

Stays:
{notes["hotels"]}

Climate:
{notes["weather"]}

Cost:
{notes["budget"]}

Draft:
{notes["itinerary"]}

Use these sections:
1. Trip summary
2. Getting there
3. Where to stay
4. Weather and packing
5. Day by day
6. Budget
7. Next steps

Be practical. Say when fares or forecasts are estimates. Use revision notes when present.
"""
    try:
        final_response = complete_text(
            "You assemble the final Your Next Travel plan.",
            prompt,
            state,
            max_tokens=PLAN_MAX_TOKENS,
            job="deep",
        )
    except Exception as exc:
        logger.exception("plan_assemble failed: %s", exc)
        final_response = notes["itinerary"] or (
            "The final plan could not be polished just now. Please retry in a minute."
        )
        failure = brief_failure(state, "plan_assemble", exc)
    else:
        failure = {}
    logger.info("plan_assemble finished")
    return {
        "final_response": final_response,
        "messages": [AIMessage(content=final_response)],
        "llm_calls": state.get("llm_calls", 0) + 1,
        **failure,
    }
