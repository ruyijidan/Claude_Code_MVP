from __future__ import annotations

import json
from pathlib import Path

from app.core.models import AgentSpec, PermissionRulesSpec, RuleSpec, TaskSpec, WorkflowSpec


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

    def load_workflow(self, name: str) -> WorkflowSpec:
        data = self._load_json_document(self.spec_root / "workflows" / f"{name}.yaml")
        return WorkflowSpec(**data)

    def load_rule(self, name: str) -> RuleSpec:
        data = self._load_json_document(self.spec_root / "rules" / f"{name}.yaml")
        return RuleSpec(**data)

    def load_permission_rules(self, name: str = "permission-rules") -> PermissionRulesSpec:
        data = self._load_json_document(self.spec_root / "rules" / f"{name}.yaml")
        return PermissionRulesSpec(**data)

    def load_template(self, name: str) -> str:
        return (self.spec_root / "templates" / f"{name}.md").read_text(encoding="utf-8")
