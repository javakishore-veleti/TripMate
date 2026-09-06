from common.constants.llm_providers import LLM_PROVIDER_GROQ, LLM_PROVIDER_OLLAMA
from common.llm_cost import model_entries
from common.log import get_logger
from common.ollama_settings import (
    configured_ollama_models,
    list_ollama_models,
    ollama_base_url,
    ollama_default_model,
)

logger = get_logger(__name__)

DEFAULT_LLM_PROVIDER = LLM_PROVIDER_OLLAMA
DEFAULT_LLM_MODEL = ollama_default_model() or "llama3.2"
GROQ_DEFAULT_MODEL = "openai/gpt-oss-120b"

_PROVIDER_LABELS = {
    LLM_PROVIDER_GROQ: "Groq",
    LLM_PROVIDER_OLLAMA: "Ollama (local)",
}

_RETIRED_MODELS = {
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
}


def _model_label(model_id: str) -> str:
    name = model_id.split("/")[-1].replace("-", " ")
    if name.lower().startswith("gpt "):
        return name.upper()
    return name.replace("qwen", "Qwen", 1)


def _is_chat_model(model_id: str) -> bool:
    lowered = model_id.lower()
    if model_id in _RETIRED_MODELS or "guard" in lowered:
        return False
    return True


def _ollama_catalog(base_url: str | None = None) -> dict:
    resolved_url = ollama_base_url(base_url)
    live_models: list[str] = []
    reachable = False
    try:
        live_models = list_ollama_models(resolved_url)
        reachable = True
    except Exception as exc:
        logger.info("ollama catalog unavailable url=%s error=%s", resolved_url, exc)

    model_ids = live_models or configured_ollama_models()
    return {
        "id": LLM_PROVIDER_OLLAMA,
        "label": _PROVIDER_LABELS[LLM_PROVIDER_OLLAMA],
        "base_url": resolved_url,
        "reachable": reachable,
        "models": [{"id": model_id, "label": model_id} for model_id in model_ids],
    }


def ui_catalog(ollama_url: str | None = None) -> dict:
    by_provider: dict[str, list[dict[str, str]]] = {}
    for model_id, meta in model_entries().items():
        if not _is_chat_model(model_id):
            continue
        provider = str((meta or {}).get("provider") or DEFAULT_LLM_PROVIDER)
        if provider == LLM_PROVIDER_OLLAMA:
            continue
        by_provider.setdefault(provider, []).append(
            {
                "id": model_id,
                "label": _model_label(model_id),
            }
        )

    providers = []
    for provider_id, models in by_provider.items():
        models.sort(key=lambda item: item["label"].lower())
        providers.append(
            {
                "id": provider_id,
                "label": _PROVIDER_LABELS.get(provider_id, provider_id),
                "models": models,
            }
        )

    providers.append(_ollama_catalog(ollama_url))
    providers.sort(key=lambda item: item["label"].lower())

    if not any(item["id"] == DEFAULT_LLM_PROVIDER for item in providers):
        providers.insert(
            0,
            {
                "id": DEFAULT_LLM_PROVIDER,
                "label": _PROVIDER_LABELS[DEFAULT_LLM_PROVIDER],
                "models": [
                    {"id": DEFAULT_LLM_MODEL, "label": _model_label(DEFAULT_LLM_MODEL)}
                ],
            },
        )

    ollama = next((item for item in providers if item["id"] == LLM_PROVIDER_OLLAMA), None)
    ollama_model = (
        ollama_default_model()
        or ((ollama or {}).get("models") or [{}])[0].get("id")
        or DEFAULT_LLM_MODEL
    )
    return {
        "default_provider": DEFAULT_LLM_PROVIDER,
        "default_model": ollama_model,
        "default_ollama_model": ollama_model,
        "ollama_base_url": ollama_base_url(ollama_url),
        "providers": providers,
    }
