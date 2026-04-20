from __future__ import annotations

from app.models.anthropic_compatible_client import AnthropicCompatibleModelClient, GLM5ModelClient
from app.models.base_client import ModelClient


def build_model_client(provider_name: str) -> ModelClient:
    selected = (provider_name or "").strip().lower()
    if selected == "glm5":
        return GLM5ModelClient()
    if selected == "anthropic_api":
        return AnthropicCompatibleModelClient()
    raise ValueError(f"unsupported model provider for local acceptance runner: {provider_name}")
