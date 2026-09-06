from overrides import override

from middleware.modules.travel_search.workflows.places_planner.main import run_places_planner
from middleware.core.services.interfaces import DashboardPlacesService


class DashboardPlacesServiceImpl(DashboardPlacesService):
    @override
    def lookup(self, user_id: str, preferences: dict, horizon: str) -> dict:
        return run_places_planner(
            user_id=user_id,
            preferences=preferences,
            horizon=horizon,
        )
