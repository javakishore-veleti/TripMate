from abc import ABC, abstractmethod
from datetime import datetime


class AppUserDao(ABC):
    @abstractmethod
    def create(self, user_id: str, email: str, password_hash: str, display_name: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def update_preferences(self, user_id: str, preferences: dict) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def record_signin(self, user_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        raise NotImplementedError


class AppSessionDao(ABC):
    @abstractmethod
    def create(self, token: str, user_id: str, expires_at: datetime) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_valid(self, token: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, token: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_for_user(self, user_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def latest_created_at(self, user_id: str) -> datetime | None:
        raise NotImplementedError


class TravelRequestDao(ABC):
    @abstractmethod
    def upsert(self, record: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def list_for_user(self, user_id: str) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_for_user(self, user_id: str, thread_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def delete_for_user(self, user_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_for_user_thread(self, user_id: str, thread_id: str) -> bool:
        raise NotImplementedError
