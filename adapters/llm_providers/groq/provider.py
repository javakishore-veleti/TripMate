import os
import re
import time

from groq import Groq, RateLimitError
from overrides import override

from adapters.llm_providers.interfaces import LLMProvider
from common.llm_catalog import GROQ_DEFAULT_MODEL
from common.llm_cost import estimate_cost_usd
from common.llm_dtos import LLMReqCtx, LLMRequest, LLMResponse, LLMStats
from common.llm_usage import add_usage
from common.log import get_logger

logger = get_logger(__name__)

_DEFAULT_MODEL = GROQ_DEFAULT_MODEL
_DEFAULT_MAX_TOKENS = 700
_RATE_LIMIT_ATTEMPTS = 3


def _retry_after_seconds(exc: Exception) -> float:
    match = re.search(r"try again in ([0-9.]+)s", str(exc), re.IGNORECASE)
    if match:
        return min(float(match.group(1)) + 0.75, 20.0)
    return 8.0


class GroqLLMProvider(LLMProvider):
    def __init__(self, request: LLMRequest | None = None, api_key: str | None = None):
        model = request.config.model if request is not None else None
        self._model = model or os.getenv("GROQ_MODEL", _DEFAULT_MODEL)
        self._client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))

    @override
    def complete(self, request: LLMRequest, ctx: LLMReqCtx) -> LLMResponse:
        config = request.config
        model = config.model or self._model
        kwargs: dict = {
            "model": model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in request.messages
            ],
        }
        if config.temperature is not None:
            kwargs["temperature"] = config.temperature
        if config.top_p is not None:
            kwargs["top_p"] = config.top_p
        kwargs["max_tokens"] = config.max_tokens or _DEFAULT_MAX_TOKENS

        logger.info("groq request model=%s max_tokens=%s", model, kwargs["max_tokens"])
        started = time.perf_counter()
        completion = None
        for attempt in range(1, _RATE_LIMIT_ATTEMPTS + 1):
            try:
                completion = self._client.chat.completions.create(**kwargs)
                break
            except RateLimitError as exc:
                if attempt == _RATE_LIMIT_ATTEMPTS:
                    logger.exception("groq rate limit exhausted model=%s", model)
                    raise
                wait = _retry_after_seconds(exc)
                logger.warning(
                    "groq rate limited model=%s attempt=%s/%s wait=%.1fs",
                    model,
                    attempt,
                    _RATE_LIMIT_ATTEMPTS,
                    wait,
                )
                time.sleep(wait)
            except Exception:
                logger.exception("groq request failed model=%s", model)
                raise
        if completion is None:
            raise RuntimeError("Groq request did not return a completion.")
        latency_ms = (time.perf_counter() - started) * 1000

        choice = completion.choices[0].message
        usage = getattr(completion, "usage", None)
        input_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
        output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
        tools_called = [
            call.function.name
            for call in (getattr(choice, "tool_calls", None) or [])
            if getattr(call, "function", None) and call.function.name
        ]

        cost_usd = estimate_cost_usd(model, input_tokens, output_tokens)
        add_usage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
        )
        ctx.request = request
        ctx.response = LLMResponse(
            text=(choice.content or "").strip(),
            raw=completion,
            stats=LLMStats(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=round(latency_ms, 2),
                tools_called=tools_called,
                cost_usd=cost_usd,
            ),
        )
        logger.info(
            "groq response model=%s latency_ms=%.0f tokens=%s/%s",
            model,
            latency_ms,
            input_tokens,
            output_tokens,
        )
        return ctx.response
