from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field, field_validator

from common.constants.llm_providers import LLM_PROVIDER_GROQ

TRequest = TypeVar("TRequest")
TCtx = TypeVar("TCtx")


class LLMMessage(BaseModel):
    role: str
    content: str


class LLMConfig(BaseModel):
    model: str | None = None
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: int | None = None
    base_url: str | None = None


class LLMRequest(BaseModel, Generic[TRequest]):
    messages: list[LLMMessage] = Field(default_factory=list)
    config: LLMConfig = Field(default_factory=LLMConfig)
    provider: str = LLM_PROVIDER_GROQ
    functional: TRequest | None = None

    @field_validator("provider", mode="before")
    @classmethod
    def default_provider(cls, value: str | None) -> str:
        if isinstance(value, str) and value.strip():
            return value.strip()
        return LLM_PROVIDER_GROQ


class LLMStats(BaseModel):
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    tools_called: list[str] = Field(default_factory=list)
    cost_usd: float | None = None


class LLMResponse(BaseModel):
    text: str = ""
    raw: Any = None
    stats: LLMStats = Field(default_factory=LLMStats)


class LLMReqCtx(BaseModel, Generic[TRequest, TCtx]):
    request: LLMRequest[TRequest]
    travelReqCtx: TCtx | None = None
    response: LLMResponse = Field(default_factory=LLMResponse)
