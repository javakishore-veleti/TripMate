from langchain_core.messages import AIMessage

from middleware.common.dtos import TravelState
from middleware.common.log import get_logger, preview

logger = get_logger(__name__)


def request_declined(state: TravelState):
    reason = state.get("final_response") or state.get("request_note") or (
        "Your Next Travel could not take this request."
    )
    logger.info("request_declined reason=%s", preview(reason))
    return {
        "final_response": reason,
        "messages": [AIMessage(content=reason)],
    }
