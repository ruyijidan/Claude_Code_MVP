from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.models import AgentSpec


class BaseAgent(ABC):
    def __init__(self, spec: AgentSpec) -> None:
        self.spec = spec

    @abstractmethod
    def run(self, state: dict) -> dict:
        raise NotImplementedError
