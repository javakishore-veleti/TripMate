from langchain_core.messages import AIMessage
from langgraph.types import interrupt

from middleware.common.dtos import TravelState
from middleware.common.log import get_logger

logger = get_logger(__name__)


def traveler_review(state: TravelState):
    logger.info("traveler_review pausing")
    proposed = state.get("proposed_action") or {}
    draft = str(proposed.get("draft_itinerary") or state.get("itinerary") or "")
    approval = str(proposed.get("approval_request") or state.get("approval_request") or "")
    review = interrupt(
        {
            "question": "Do you approve this trip draft?",
            "draft_itinerary": draft,
            "approval_request": approval,
            "proposed_action": proposed,
            "selected_specialists": state.get("selected_specialists", []),
            "coordinator_notes": state.get("coordinator_notes", ""),
            "expected_response": {
                "approved": True,
                "feedback": "Optional revision notes",
            },
        }
    )
    if not isinstance(review, dict):
        review = {"approved": bool(review), "feedback": ""}
    approved = bool(review.get("approved", False))
    feedback = str(review.get("feedback", "")).strip()
    logger.info("traveler_review resumed approved=%s", approved)
    return {
        "approved": approved,
        "traveler_feedback": feedback,
        "messages": [AIMessage(content="Traveler review recorded.")],
    }
