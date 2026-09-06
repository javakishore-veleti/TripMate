from middleware.modules.shared.services.objects import ServicesObjectFactory
from middleware.modules.shared.services.service_names import SERVICE_DASHBOARD_PLACES


class PlacesFacade:
    def __init__(self):
        self._service = ServicesObjectFactory.get_service(SERVICE_DASHBOARD_PLACES)

    def lookup(self, user_id: str, preferences: dict, horizon: str) -> dict:
        return self._service.lookup(user_id=user_id, preferences=preferences, horizon=horizon)
