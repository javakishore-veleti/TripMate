from overrides import override

from middleware.adapters.agentic.objects import AgenticAdapterObjectFactory
from middleware.modules.shared.services.interfaces import DashboardPlacesService


class DashboardPlacesServiceImpl(DashboardPlacesService):
    @override
    def lookup(self, user_id: str, preferences: dict, horizon: str) -> dict:
        return AgenticAdapterObjectFactory.places_planner(
            user_id=user_id,
            preferences=preferences,
            horizon=horizon,
        )
