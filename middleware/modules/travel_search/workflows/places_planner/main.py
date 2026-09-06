from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from middleware.modules.travel_search.workflows.places_planner.tasks import (
    this_month_task,
    this_quarter_task,
    this_week_task,
)
from middleware.common.constants.llm_providers import LLM_PROVIDER_GROQ, LLM_PROVIDER_OLLAMA
from middleware.common.llm_catalog import ui_catalog
from middleware.common.log import get_logger
from middleware.common.ollama_settings import ollama_base_url, ollama_default_model
from middleware.common.user_preferences import format_place, normalize_preferences

logger = get_logger(__name__)

_TASK_BY_HORIZON = {
    "week": "this_week",
    "month": "this_month",
    "quarter": "this_quarter",
}


class PlacesPlannerState(TypedDict, total=False):
    horizon: str
    user_id: str
    user_preferences: dict
    llm_provider: str
    llm_model: str
    llm_base_url: str
    window: str
    radius_miles: int
    places: list[str]
    events: list[dict]


def _route_horizon(state: PlacesPlannerState) -> str:
    return _TASK_BY_HORIZON.get(str(state.get("horizon") or "month"), "this_month")


def _pick_horizon(state: PlacesPlannerState) -> dict:
    return {}


def _build_graph():
    graph = StateGraph(PlacesPlannerState)
    graph.add_node("pick_horizon", _pick_horizon)
    graph.add_node("this_week", this_week_task)
    graph.add_node("this_month", this_month_task)
    graph.add_node("this_quarter", this_quarter_task)
    graph.add_edge(START, "pick_horizon")
    graph.add_conditional_edges(
        "pick_horizon",
        _route_horizon,
        {
            "this_week": "this_week",
            "this_month": "this_month",
            "this_quarter": "this_quarter",
        },
    )
    graph.add_edge("this_week", END)
    graph.add_edge("this_month", END)
    graph.add_edge("this_quarter", END)
    return graph.compile()


_places_planner_graph = None


def places_planner_graph():
    global _places_planner_graph
    if _places_planner_graph is None:
        _places_planner_graph = _build_graph()
    return _places_planner_graph


def resolve_job_llm(
    preferences: dict,
    job: str = "reason",
    default_provider: str = "",
    default_model: str = "",
    default_url: str = "",
) -> tuple[str, str, str]:
    prefs = normalize_preferences(preferences)
    chosen = (prefs.get("llm_jobs") or {}).get(job) or {}
    provider = str(
        chosen.get("provider")
        or default_provider
        or prefs.get("llm_provider")
        or LLM_PROVIDER_OLLAMA
    ).strip() or LLM_PROVIDER_OLLAMA
    model = str(
        chosen.get("model") or default_model or prefs.get("llm_model") or ""
    ).strip()
    base_url = str(
        chosen.get("base_url") or default_url or prefs.get("llm_base_url") or ""
    ).strip()
    catalog = ui_catalog(base_url or None)
    ollama = next((item for item in catalog["providers"] if item["id"] == LLM_PROVIDER_OLLAMA), None)
    if provider == LLM_PROVIDER_OLLAMA:
        base_url = base_url or ollama_base_url()
        model = (
            model
            or ollama_default_model()
            or ((ollama or {}).get("models") or [{}])[0].get("id")
            or ""
        )
        if not model:
            raise ValueError(
                "No local Ollama model is available. Pull one with `ollama pull` "
                "or pick a cloud model on Account."
            )
        return provider, model, base_url
    if provider == LLM_PROVIDER_GROQ and not model:
        groq = next((item for item in catalog["providers"] if item["id"] == LLM_PROVIDER_GROQ), None)
        model = ((groq or {}).get("models") or [{}])[0].get("id") or ""
    if not model:
        raise ValueError("Pick a model on your account first.")
    return provider, model, base_url


def resolve_dashboard_llm(preferences: dict) -> tuple[str, str, str]:
    return resolve_job_llm(preferences, "reason")


def resolve_brief_jobs(
    preferences: dict,
    default_provider: str = "",
    default_model: str = "",
    default_url: str = "",
) -> dict:
    jobs = {}
    for job in ("classify", "reason", "deep"):
        provider, model, base_url = resolve_job_llm(
            preferences,
            job,
            default_provider=default_provider,
            default_model=default_model,
            default_url=default_url,
        )
        jobs[job] = {"provider": provider, "model": model, "base_url": base_url}
    return jobs


def run_places_planner(user_id: str, preferences: dict, horizon: str) -> dict:
    prefs = normalize_preferences(preferences)
    if not prefs["places"]:
        raise ValueError("Add up to five cities on your account first.")
    jobs = resolve_brief_jobs(prefs)
    nearby = jobs["reason"]
    logger.info(
        "places planner start horizon=%s provider=%s model=%s",
        horizon,
        nearby["provider"],
        nearby["model"],
    )
    result = places_planner_graph().invoke(
        {
            "horizon": horizon if horizon in _TASK_BY_HORIZON else "month",
            "user_id": user_id,
            "user_preferences": prefs,
            "llm_provider": nearby["provider"],
            "llm_model": nearby["model"],
            "llm_base_url": nearby["base_url"],
            "llm_jobs": jobs,
            "events": [],
            "places": [format_place(place) for place in prefs["places"]],
            "radius_miles": prefs["event_radius_miles"],
        }
    )
    return {
        "horizon": result.get("horizon") or horizon,
        "window": result.get("window") or "",
        "radius_miles": result.get("radius_miles") or prefs["event_radius_miles"],
        "places": result.get("places") or [],
        "events": result.get("events") or [],
        "llm_provider": nearby["provider"],
        "llm_model": nearby["model"],
    }
