from middleware.modules.shared.services.interfaces import PlanDeskService
from middleware.modules.shared.services.objects import ServicesObjectFactory
from middleware.modules.shared.services.service_names import SERVICE_PLAN_DESK


class PlanDeskFacade:
    def __init__(self, service: PlanDeskService | None = None):
        self._service: PlanDeskService = service or ServicesObjectFactory.get_service(SERVICE_PLAN_DESK)

    def lookup(self, user_id: str, preferences: dict) -> dict:
        return self._service.lookup(user_id=user_id, preferences=preferences)
