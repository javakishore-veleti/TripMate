from langchain_core.messages import AIMessage

from common.dtos import TravelState
from common.log import get_logger, preview

logger = get_logger(__name__)


def guardrail_blocked_agent(state: TravelState):
    reason = state.get("final_response") or state.get("guardrail_reason") or (
        "This request was blocked by the travel input guardrail."
    )
    logger.info("guardrail_blocked reason=%s", preview(reason))
    return {
        "final_response": reason,
        "messages": [AIMessage(content=reason)],
    }
