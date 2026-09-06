from abc import ABC, abstractmethod
from typing import Generic

from middleware.common.constants.llm_roles import LLM_ROLE_SYSTEM, LLM_ROLE_USER
from middleware.common.llm_dtos import LLMMessage, LLMReqCtx, LLMRequest, LLMResponse, TCtx, TRequest


class LLMProvider(ABC, Generic[TRequest, TCtx]):
    """Vendor chat client. LangGraph, Google ADK, Strands, and others call this."""

    @abstractmethod
    def complete(
        self,
        request: LLMRequest[TRequest],
        ctx: LLMReqCtx[TRequest, TCtx],
    ) -> LLMResponse:
        raise NotImplementedError

    def complete_prompt(self, system_prompt: str, user_prompt: str) -> str:
        request = LLMRequest[TRequest](
            messages=[
                LLMMessage(role=LLM_ROLE_SYSTEM, content=system_prompt),
                LLMMessage(role=LLM_ROLE_USER, content=user_prompt),
            ]
        )
        llm_ctx = LLMReqCtx[TRequest, TCtx](request=request)
        return self.complete(request, llm_ctx).text
