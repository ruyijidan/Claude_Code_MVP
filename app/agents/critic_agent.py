from __future__ import annotations

from app.agents.base_agent import BaseAgent
from app.core.models import RuleSpec


class CriticAgent(BaseAgent):
    def __init__(self, spec, rule_spec: RuleSpec | None = None) -> None:
        super().__init__(spec)
        self.rule_spec = rule_spec

    def run(self, state: dict) -> dict:
        issues = []
        if state.get("test_result") != "passed":
            issues.append("tests_failed")
        if state.get("verification_errors"):
            issues.extend(state["verification_errors"])
        if state.get("gate_failures"):
            issues.extend(state["gate_failures"])
        if self.rule_spec is not None:
            issues.extend(self._apply_rule(state))
        return {"critic_issues": issues}

    def _apply_rule(self, state: dict) -> list[str]:
        task_spec = state.get("task_spec")
        if task_spec is None or task_spec.name not in self.rule_spec.applies_to:
            return []
        changed_files = state.get("changed_files", [])
        if not isinstance(changed_files, list) or not changed_files:
            return [self.rule_spec.failure_message]
        return []
