from __future__ import annotations

from abc import ABC, abstractmethod


class BaseTool(ABC):
    name: str

    @abstractmethod
    def invoke(self, **kwargs) -> dict:
        raise NotImplementedError
