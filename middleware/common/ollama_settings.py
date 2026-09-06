import os

import requests

DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"


def ollama_base_url(override: str | None = None) -> str:
    raw = (
        (override or "").strip()
        or (os.getenv("OLLAMA_BASE_URL") or "").strip()
        or (os.getenv("OLLAMA_HOST") or "").strip()
        or DEFAULT_OLLAMA_BASE_URL
    )
    if "://" not in raw:
        raw = f"http://{raw}"
    return raw.rstrip("/")


def ollama_default_model() -> str:
    return (os.getenv("OLLAMA_MODEL") or "").strip()


_SKIP_MODELS = ("embed", "nomic", "codellama", "guard")
_CHAT_FIRST = ("llama3.2", "llama3", "gemma", "qwen", "mistral", "phi")


def prefer_chat_model(model_ids: list[str]) -> str:
    usable = [
        name
        for name in model_ids
        if name and not any(skip in name.lower() for skip in _SKIP_MODELS)
    ]
    for prefix in _CHAT_FIRST:
        for name in usable:
            if name.lower().startswith(prefix):
                return name
    return usable[0] if usable else (model_ids[0] if model_ids else "")


def configured_ollama_models() -> list[str]:
    raw = (os.getenv("OLLAMA_MODELS") or "").strip()
    names = [part.strip() for part in raw.split(",") if part.strip()]
    default = ollama_default_model()
    if default and default not in names:
        names.insert(0, default)
    return names


def list_ollama_models(base_url: str | None = None, timeout: float = 1.5) -> list[str]:
    url = f"{ollama_base_url(base_url)}/api/tags"
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    payload = response.json() if response.content else {}
    names: list[str] = []
    for item in payload.get("models") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or item.get("model") or "").strip()
        if name:
            names.append(name)
    return sorted(set(names), key=str.lower)
