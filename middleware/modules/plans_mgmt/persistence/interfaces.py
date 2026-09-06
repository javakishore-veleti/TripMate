from abc import ABC, abstractmethod


class DraftPlanDao(ABC):
    @abstractmethod
    def upsert(self, record: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_for_user(self, user_id: str, thread_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def delete_for_user_thread(self, user_id: str, thread_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def delete_for_user(self, user_id: str) -> None:
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
