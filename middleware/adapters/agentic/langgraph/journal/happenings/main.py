from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from middleware.adapters.agentic.langgraph.dashboard.places_planner.main import resolve_brief_jobs
from middleware.adapters.agentic.langgraph.journal.happenings.tasks.briefs import (
    food_brief,
    ideas_brief,
    pack_brief,
)
from middleware.adapters.agentic.langgraph.journal.happenings.tasks.classify import classify_traveler
from middleware.adapters.agentic.langgraph.journal.happenings.tasks.happenings import (
    collect_month_happenings,
)
from middleware.common.log import get_logger
from middleware.common.user_preferences import format_place, normalize_preferences
from middleware.modules.preferences_mgmt.persistence.store import selected_skill_names

logger = get_logger(__name__)


class HappeningsState(TypedDict, total=False):
    expand: bool
    year: int
    month: int
    user_id: str
    user_preferences: dict
    skill_names: list[str]
    llm_provider: str
    llm_model: str
    llm_base_url: str
    llm_jobs: dict
    lens: str
    classify_note: str
    window: str
    radius_miles: int
    places: list[str]
    events: list[dict]
    pack: str
    food: str
    ideas: str


def _after_happenings(state: HappeningsState) -> str:
    return "pack" if state.get("expand") else END


def _build_graph():
    graph = StateGraph(HappeningsState)
    graph.add_node("classify", classify_traveler)
    graph.add_node("happenings", collect_month_happenings)
    graph.add_node("pack", pack_brief)
    graph.add_node("food", food_brief)
    graph.add_node("ideas", ideas_brief)
    graph.add_edge(START, "classify")
    graph.add_edge("classify", "happenings")
    graph.add_conditional_edges(
        "happenings",
        _after_happenings,
        {"pack": "pack", END: END},
    )
    graph.add_edge("pack", "food")
    graph.add_edge("food", "ideas")
    graph.add_edge("ideas", END)
    return graph.compile()


_graph = None


def happenings_graph():
    global _graph
    if _graph is None:
        _graph = _build_graph()
    return _graph


def run_journal_happenings(
    user_id: str,
    preferences: dict,
    expand: bool = False,
    year: int | None = None,
    month: int | None = None,
) -> dict:
    prefs = normalize_preferences(preferences)
    if not prefs["places"]:
        raise ValueError("Add up to five cities on your account first.")
    jobs = resolve_brief_jobs(prefs)
    nearby = jobs["reason"]
    skills = selected_skill_names(user_id)
    logger.info(
        "journal happenings start expand=%s jobs=%s skills=%s",
        expand,
        {key: f"{item['provider']}:{item['model']}" for key, item in jobs.items()},
        skills,
    )
    result = happenings_graph().invoke(
        {
            "expand": bool(expand),
            "year": year or 0,
            "month": month or 0,
            "user_id": user_id,
            "user_preferences": prefs,
            "skill_names": skills,
            "llm_provider": nearby["provider"],
            "llm_model": nearby["model"],
            "llm_base_url": nearby["base_url"],
            "llm_jobs": jobs,
            "places": [format_place(place) for place in prefs["places"]],
            "radius_miles": prefs["event_radius_miles"],
            "events": [],
            "pack": "",
            "food": "",
            "ideas": "",
        }
    )
    return {
        "expanded": bool(expand),
        "year": result.get("year"),
        "month": result.get("month"),
        "window": result.get("window") or "",
        "radius_miles": result.get("radius_miles") or prefs["event_radius_miles"],
        "places": result.get("places") or [],
        "skill_names": skills,
        "lens": result.get("lens") or "mix",
        "classify_note": result.get("classify_note") or "",
        "events": result.get("events") or [],
        "pack": result.get("pack") or "",
        "food": result.get("food") or "",
        "ideas": result.get("ideas") or "",
        "llm_jobs": {
            key: {"provider": item["provider"], "model": item["model"]}
            for key, item in jobs.items()
        },
        "llm_provider": nearby["provider"],
        "llm_model": nearby["model"],
    }
