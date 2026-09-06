from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TRequest = TypeVar("TRequest")
TCtx = TypeVar("TCtx")


class AgenticFrameworkAdapter(ABC, Generic[TRequest, TCtx]):
    @abstractmethod
    def execute(self, request: TRequest, ctx: TCtx) -> int:
        raise NotImplementedError
