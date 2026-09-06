from langchain_core.messages import AIMessage

from adapters.agentic.langgraph.agents.utils import (
    PLAN_MAX_TOKENS,
    complete_text,
    specialist_notes,
)
from common.dtos import TravelState
from common.log import get_logger

logger = get_logger(__name__)


def final_agent(state: TravelState):
    logger.info("final_agent started approved=%s", state.get("approved", False))
    if state.get("approved", False):
        review_instruction = (
            "The user approved the draft. Preserve its decisions while polishing it."
        )
    else:
        review_instruction = f"""
The user requested a revision. Apply this feedback carefully:
{state.get('human_feedback', '') or 'Improve the draft before finalizing it.'}
"""

    notes = specialist_notes(state)
    final_prompt = f"""
Generate the final travel response for the user.

Human Review:
{review_instruction}

User Request:
{state['user_query']}

Supervisor Constraints:
{state.get('trip_constraints', {})}

Flights:
{notes['flights']}

Hotels:
{notes['hotels']}

Weather:
{notes['weather']}

Budget Analysis:
{notes['budget']}

Draft Itinerary:
{notes['itinerary']}

Format the final answer beautifully using these sections:
1. Trip Summary
2. Flight Information
3. Hotel Suggestions
4. Weather Information
5. Day-by-Day Itinerary
6. Estimated Budget
7. Final Recommendations

Important:
- Be clear and practical.
- Mention that live flight APIs may not provide ticket prices when pricing is unavailable.
- Include weather-based travel advice.
- Keep the response useful for real travel planning.
- Incorporate the human feedback when revision was requested.
"""

    try:
        final_response = complete_text(
            "You are a professional AI travel booking assistant.",
            final_prompt,
            state,
            max_tokens=PLAN_MAX_TOKENS,
        )
    except Exception as exc:
        logger.exception("final_agent failed: %s", exc)
        final_response = notes["itinerary"] or (
            "The final plan could not be polished because the model rate "
            "limit was reached. Please retry in a minute."
        )
    logger.info("final_agent finished")

    return {
        "final_response": final_response,
        "messages": [AIMessage(content=final_response)],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
