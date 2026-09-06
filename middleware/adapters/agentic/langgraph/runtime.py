from collections.abc import Callable
from typing import Any

from middleware.adapters.agentic.langgraph.llm_text import empty_constraints
from middleware.common.dtos import TravelReqCtx, TravelState
from middleware.common.log import get_logger

logger = get_logger(__name__)

DEFAULT_MAX_STEPS = 16
STEP_HALTED = "halted"

NodeFn = Callable[[TravelState], dict]


def graph_config(ctx: TravelReqCtx) -> dict:
    return {
        "configurable": {
            "thread_id": ctx.thread_id,
            "checkpoint_ns": "",
        }
    }


def normalize_constraints(raw) -> dict[str, Any]:
    constraints = empty_constraints()
    if not isinstance(raw, dict):
        return constraints
    for key, default in constraints.items():
        value = raw.get(key, default)
        if key == "special_preferences":
            constraints[key] = [str(item).strip() for item in value] if isinstance(value, list) else []
        else:
            constraints[key] = str(value or "").strip()
    return constraints


def brief_failure(state: TravelState, node: str, exc: Exception) -> dict:
    return {
        "error_count": int(state.get("error_count") or 0) + 1,
        "last_error": {"type": "exception", "node": node, "detail": str(exc)},
    }


def halt_node(state: TravelState) -> dict:
    note = "This plan stopped after too many steps."
    return {
        "current_step": STEP_HALTED,
        "request_note": note,
        "final_response": state.get("itinerary") or state.get("final_response") or note,
        "last_error": state.get("last_error")
        or {"type": "max_steps", "detail": note},
    }


def with_runtime(name: str, fn: NodeFn) -> NodeFn:
    def node(state: TravelState) -> dict:
        steps = int(state.get("step_count") or 0) + 1
        limit = int(state.get("max_steps") or DEFAULT_MAX_STEPS)
        if steps > limit:
            logger.warning("graph halted node=%s steps=%s limit=%s", name, steps, limit)
            return {
                "step_count": steps,
                "current_step": STEP_HALTED,
                "last_error": {"type": "max_steps", "node": name, "detail": "Too many steps."},
            }
        try:
            update = fn(state) or {}
        except Exception as exc:
            logger.exception("graph node failed node=%s: %s", name, exc)
            return {
                "step_count": steps,
                "current_step": "error",
                "error_count": int(state.get("error_count") or 0) + 1,
                "last_error": {"type": "exception", "node": name, "detail": str(exc)},
            }
        if not isinstance(update, dict):
            update = {}
        update.setdefault("current_step", name)
        update["step_count"] = steps
        return update

    return node


def is_halted(state: TravelState) -> bool:
    return state.get("current_step") == STEP_HALTED
