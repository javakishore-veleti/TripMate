from middleware.modules.travel_search.workflows.places_planner.tasks.common import collect_events


def this_week_task(state: dict) -> dict:
    return collect_events(state, "week")
