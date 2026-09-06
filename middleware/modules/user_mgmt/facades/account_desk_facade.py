from middleware.modules.shared.services.interfaces import AccountDeskService
from middleware.modules.shared.services.objects import ServicesObjectFactory
from middleware.modules.shared.services.service_names import SERVICE_ACCOUNT_DESK


class AccountDeskFacade:
    def __init__(self, service: AccountDeskService | None = None):
        self._service: AccountDeskService = service or ServicesObjectFactory.get_service(
            SERVICE_ACCOUNT_DESK
        )

    def lookup(self, user_id: str, preferences: dict, display_name: str = "") -> dict:
        return self._service.lookup(
            user_id=user_id,
            preferences=preferences,
            display_name=display_name,
        )
