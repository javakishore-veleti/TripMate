from middleware.adapters.agentic.langgraph.dashboard.places_planner.tasks.common import collect_events


def this_month_task(state: dict) -> dict:
    return collect_events(state, "month")
