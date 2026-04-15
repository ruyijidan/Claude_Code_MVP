from __future__ import annotations

import json
from pathlib import Path

from app.core.models import AgentSpec, TaskSpec


class SpecLoader:
    """Loads JSON-compatible YAML files from the specs directory."""

    def __init__(self, spec_root: Path) -> None:
        self.spec_root = spec_root

    def _load_json_document(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def load_task(self, name: str) -> TaskSpec:
        data = self._load_json_document(self.spec_root / "tasks" / f"{name}.yaml")
        return TaskSpec(**data)

    def load_agent(self, name: str) -> AgentSpec:
        data = self._load_json_document(self.spec_root / "agents" / f"{name}.yaml")
        return AgentSpec(**data)
