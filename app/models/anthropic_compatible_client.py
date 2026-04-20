from __future__ import annotations

import json
import os
from pathlib import Path

from app.models.base_client import ModelClient
from app.runtime.api_adapter import AnthropicCompatibleAdapter


class AnthropicCompatibleModelClient(ModelClient):
    provider_name = "anthropic_api"

    def __init__(self, *, provider_alias: str | None = None) -> None:
        self.adapter = AnthropicCompatibleAdapter(provider_alias=provider_alias)
        self.provider_name = provider_alias or self.provider_name

    def generate(self, prompt: str) -> str:
        code, output, _command = self.adapter.execute_prompt(prompt, Path("."))
        if code != 0:
            raise RuntimeError(output)
        payload = json.loads(output)
        result = payload.get("result", "")
        if not isinstance(result, str) or not result.strip():
            raise RuntimeError(f"{self.provider_name} returned an empty result payload")
        return result


class GLM5ModelClient(AnthropicCompatibleModelClient):
    provider_name = "glm5"

    def __init__(self) -> None:
        super().__init__(provider_alias=self.provider_name)
