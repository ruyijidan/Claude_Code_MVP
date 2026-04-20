from __future__ import annotations

from typing import Protocol


class ModelClient(Protocol):
    provider_name: str

    def generate(self, prompt: str) -> str:
        ...
