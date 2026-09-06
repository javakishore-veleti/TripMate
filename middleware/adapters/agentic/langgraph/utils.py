from typing import Any, Iterable

from middleware.adapters.agentic.langgraph.specialists.ids import TRAVELER_REVIEW

_STATUS_MESSAGES = {
    "Request accepted for trip planning.",
    "Trip research plan is ready.",
    "Air research added.",
    "Stay research added.",
    "Climate brief added.",
    "Cost review added.",
    "Trip draft is ready for review.",
    "Traveler review recorded.",
}


def _interrupt_payload(result: dict[str, Any]) -> dict[str, Any] | None:
    interrupts = result.get("__interrupt__") or ()
    if not interrupts:
        return None
    first = interrupts[0]
    value = getattr(first, "value", first)
    return value if isinstance(value, dict) else None


def _message_text(message: Any) -> str:
    content = getattr(message, "content", message)
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("text") or ""))
        return "".join(parts).strip()
    return str(content or "").strip()


def _serialize_result(
    result: dict[str, Any],
    thread_id: str,
    next_nodes: Iterable[str] | None = None,
) -> dict[str, Any]:
    messages = result.get("messages", [])
    last_message = _message_text(messages[-1]) if messages else ""
    if last_message in _STATUS_MESSAGES:
        last_message = ""

    interrupt_payload = _interrupt_payload(result)
    paused = interrupt_payload is not None or TRAVELER_REVIEW in tuple(next_nodes or ())

    itinerary = (
        interrupt_payload.get("draft_itinerary", "")
        if interrupt_payload
        else result.get("itinerary", "")
    )
    answer = result.get("final_response") or itinerary or last_message
    if paused:
        answer = itinerary or result.get("itinerary", "") or last_message

    specialists = result.get("selected_specialists") or result.get("selected_agents") or []
    notes = result.get("coordinator_notes") or result.get("supervisor_reasoning") or ""
    accepted = result.get("request_accepted")
    if accepted is None:
        accepted = result.get("guardrail_allowed", True)
    note = result.get("request_note") or result.get("guardrail_reason") or ""

    return {
        "thread_id": thread_id,
        "answer": answer,
        "requires_approval": paused,
        "approval_request": (
            interrupt_payload.get("approval_request", "")
            if interrupt_payload
            else result.get("approval_request", "")
        ),
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "weather_results": result.get("weather_results", ""),
        "budget_results": result.get("budget_results", ""),
        "itinerary": itinerary or result.get("itinerary", ""),
        "selected_specialists": specialists,
        "trip_constraints": result.get("trip_constraints", {}),
        "coordinator_notes": notes,
        "request_accepted": accepted,
        "request_note": note,
        "approved": result.get("approved"),
        "traveler_feedback": result.get("traveler_feedback") or result.get("human_feedback", ""),
        "llm_calls": result.get("llm_calls", 0),
    }
