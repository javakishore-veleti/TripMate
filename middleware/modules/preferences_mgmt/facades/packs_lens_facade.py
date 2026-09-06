from middleware.modules.shared.services.interfaces import PacksLensService
from middleware.modules.shared.services.objects import ServicesObjectFactory
from middleware.modules.shared.services.service_names import SERVICE_PACKS_LENS


class PacksLensFacade:
    def __init__(self, service: PacksLensService | None = None):
        self._service: PacksLensService = service or ServicesObjectFactory.get_service(SERVICE_PACKS_LENS)

    def lookup(self, user_id: str, preferences: dict) -> dict:
        return self._service.lookup(user_id=user_id, preferences=preferences)
