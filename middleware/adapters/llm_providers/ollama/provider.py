import time

import requests
from overrides import override

from middleware.adapters.llm_providers.interfaces import LLMProvider
from middleware.common.llm_dtos import LLMReqCtx, LLMRequest, LLMResponse, LLMStats
from middleware.common.llm_usage import add_usage
from middleware.common.log import get_logger
from middleware.common.ollama_settings import ollama_base_url, ollama_default_model

logger = get_logger(__name__)

_DEFAULT_MAX_TOKENS = 700
_DEFAULT_TIMEOUT_SECONDS = 180


class OllamaLLMProvider(LLMProvider):
    def __init__(self, request: LLMRequest | None = None, base_url: str | None = None):
        model = request.config.model if request is not None else None
        configured_url = request.config.base_url if request is not None else None
        self._model = model or ollama_default_model()
        self._base_url = ollama_base_url(configured_url or base_url)

    @override
    def complete(self, request: LLMRequest, ctx: LLMReqCtx) -> LLMResponse:
        config = request.config
        model = config.model or self._model
        if not model:
            raise ValueError(
                "No Ollama model selected. Pull a model with `ollama pull` "
                "or set OLLAMA_MODEL."
            )
        base_url = ollama_base_url(config.base_url or self._base_url)
        payload: dict = {
            "model": model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in request.messages
            ],
            "stream": False,
            "options": {},
        }
        if config.temperature is not None:
            payload["options"]["temperature"] = config.temperature
        if config.top_p is not None:
            payload["options"]["top_p"] = config.top_p
        payload["options"]["num_predict"] = config.max_tokens or _DEFAULT_MAX_TOKENS

        logger.info("ollama request url=%s model=%s", base_url, model)
        started = time.perf_counter()
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json=payload,
                timeout=_DEFAULT_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
        except requests.ConnectionError as exc:
            raise RuntimeError(
                f"Ollama is not reachable at {base_url}. Start Ollama or set "
                "OLLAMA_BASE_URL to the host that is running it."
            ) from exc
        except requests.HTTPError as exc:
            detail = ""
            if exc.response is not None:
                detail = (exc.response.text or "").strip()[:240]
            raise RuntimeError(
                f"Ollama request failed at {base_url} for model {model}: "
                f"{detail or exc}"
            ) from exc

        body = response.json() if response.content else {}
        latency_ms = (time.perf_counter() - started) * 1000
        message = body.get("message") or {}
        text = str(message.get("content") or "").strip()
        input_tokens = int(body.get("prompt_eval_count") or 0)
        output_tokens = int(body.get("eval_count") or 0)
        add_usage(input_tokens=input_tokens, output_tokens=output_tokens, cost_usd=0.0)

        ctx.request = request
        ctx.response = LLMResponse(
            text=text,
            raw=body,
            stats=LLMStats(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=round(latency_ms, 2),
                cost_usd=0.0,
            ),
        )
        logger.info(
            "ollama response url=%s model=%s latency_ms=%.0f tokens=%s/%s",
            base_url,
            model,
            latency_ms,
            input_tokens,
            output_tokens,
        )
        return ctx.response
