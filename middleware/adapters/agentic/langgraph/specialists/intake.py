from langchain_core.messages import AIMessage

from middleware.adapters.agentic.langgraph.llm_text import JSON_MAX_TOKENS, complete_text, json_from_llm
from middleware.adapters.agentic.langgraph.runtime import brief_failure
from middleware.common.dtos import TravelState
from middleware.common.log import get_logger, preview

logger = get_logger(__name__)


def intake(state: TravelState):
    query = state["user_query"]
    llm_calls = state.get("llm_calls", 0)
    failure = {}
    logger.info("intake started query=%s", preview(query))
    prompt = f"""
Decide if this is a travel-planning or travel-information request.

Accept destinations, transport, stays, weather, budgets, visas, food,
packing, or day plans. Reject unrelated work and harmful or illegal asks.
Do not reject a real trip just because a few details are missing.

Return JSON only:
{{
  "accepted": true,
  "note": ""
}}

Traveler request:
{query}
"""
    try:
        raw = complete_text(
            "You decide whether Your Next Travel should take a request. Return JSON only.",
            prompt,
            state,
            max_tokens=JSON_MAX_TOKENS,
            job="classify",
        )
        parsed = json_from_llm(raw)
        accepted = bool(parsed.get("accepted", True))
        note = str(parsed.get("note", "")).strip()
        llm_calls += 1
    except Exception as exc:
        logger.warning("intake fallback used: %s", exc)
        accepted = True
        note = "Intake could not parse the model reply, so the request continues."
        failure = brief_failure(state, "intake", exc)

    if not accepted:
        reason = note or (
            "Your Next Travel only helps with trips. Ask about a place to go, "
            "how to get there, where to stay, weather, budget, or a day plan."
        )
        logger.info("intake declined reason=%s", preview(reason))
        return {
            "request_accepted": False,
            "request_note": reason,
            "selected_specialists": [],
            "coordinator_notes": reason,
            "final_response": reason,
            "messages": [AIMessage(content=reason)],
            "llm_calls": llm_calls,
            **failure,
        }

    return {
        "request_accepted": True,
        "request_note": note,
        "messages": [AIMessage(content="Request accepted for trip planning.")],
        "llm_calls": llm_calls,
        **failure,
    }
