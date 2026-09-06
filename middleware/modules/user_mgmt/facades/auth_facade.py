from middleware.modules.shared.services.objects import ServicesObjectFactory
from middleware.modules.shared.services.service_names import SERVICE_AUTH


class AuthFacade:
    def __init__(self):
        self._service = ServicesObjectFactory.get_service(SERVICE_AUTH)

    def signup(self, email: str, password: str, display_name: str = "") -> dict:
        return self._service.signup(email, password, display_name)

    def signin(self, email: str, password: str) -> dict:
        return self._service.signin(email, password)

    def create_session(self, user_id: str) -> str:
        return self._service.create_session(user_id)

    def issue_access_token(self, user: dict) -> str:
        return self._service.issue_access_token(user)

    def signout(self, token: str | None) -> None:
        return self._service.signout(token)

    def save_preferences(self, user_id: str, preferences: dict) -> dict:
        return self._service.save_preferences(user_id, preferences)

    def delete_account(self, user_id: str) -> None:
        return self._service.delete_account(user_id)
