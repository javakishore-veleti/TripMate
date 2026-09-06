from abc import ABC, abstractmethod


class PipelineSnapshotDao(ABC):
    @abstractmethod
    def get_for_user(self, user_id: str, pipeline_key: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def upsert(self, record: dict) -> dict:
        raise NotImplementedError
