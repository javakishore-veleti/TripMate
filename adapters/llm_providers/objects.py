import os

from adapters.llm_providers.groq.provider import GroqLLMProvider
from adapters.llm_providers.interfaces import LLMProvider
from adapters.llm_providers.ollama.provider import OllamaLLMProvider
from adapters.llm_providers.provider_names import PROVIDER_GROQ, PROVIDER_OLLAMA
from common.llm_dtos import LLMRequest
from common.ollama_settings import ollama_base_url

provider_instances = {}
provider_names_to_classes = {
    PROVIDER_GROQ: GroqLLMProvider,
    PROVIDER_OLLAMA: OllamaLLMProvider,
}


class LLMProviderObjectFactory:
    @staticmethod
    def get_provider(request: LLMRequest) -> LLMProvider:
        name = (
            (request.provider or "").strip()
            or os.getenv("LLM_PROVIDER", "").strip()
            or PROVIDER_GROQ
        )
        if name not in provider_names_to_classes:
            raise ValueError(f"LLM provider {name} not found")
        cache_key = (name, request.config.model, ollama_base_url(request.config.base_url))
        if cache_key not in provider_instances:
            provider_instances[cache_key] = provider_names_to_classes[name](request)
        return provider_instances[cache_key]
