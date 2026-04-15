from __future__ import annotations

from collections import defaultdict
from typing import Callable


class EventBus:
    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[[dict], None]]] = defaultdict(list)

    def subscribe(self, topic: str, listener: Callable[[dict], None]) -> None:
        self._listeners[topic].append(listener)

    def publish(self, topic: str, event: dict) -> None:
        for listener in self._listeners[topic]:
            listener(event)
