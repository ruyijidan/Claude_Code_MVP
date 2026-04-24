from __future__ import annotations

from collections.abc import Iterable

from app.agents.base_agent import BaseAgent
from app.core.models import RuleSpec


class CriticAgent(BaseAgent):
    def __init__(self, spec, rule_spec: RuleSpec | Iterable[RuleSpec] | None = None) -> None:
        super().__init__(spec)
        if rule_spec is None:
            self.rule_specs: list[RuleSpec] = []
        elif isinstance(rule_spec, RuleSpec):
            self.rule_specs = [rule_spec]
        else:
            self.rule_specs = list(rule_spec)

    def run(self, state: dict) -> dict:
        issues = []
        if state.get("test_result") != "passed":
            issues.append("tests_failed")
        if state.get("verification_errors"):
            issues.extend(state["verification_errors"])
        if state.get("gate_failures"):
            issues.extend(state["gate_failures"])
        rule_hits = self._apply_rules(state)
        issues.extend(hit["message"] for hit in rule_hits)
        return {"critic_issues": issues, "critic_rule_hits": rule_hits}

    def _apply_rules(self, state: dict) -> list[dict]:
        task_spec = state.get("task_spec")
        if task_spec is None:
            return []
        changed_files = state.get("changed_files", [])
        prompt = state.get("request", {}).get("feature_request", "").lower()
        if not isinstance(changed_files, list):
            changed_files = []

        hits: list[dict] = []
        for rule in self.rule_specs:
            if task_spec.name not in rule.applies_to:
                continue
            failed_checks = self._failed_checks(rule, changed_files, prompt)
            if not failed_checks:
                continue
            hits.append(
                {
                    "rule": rule.name,
                    "intent": rule.intent,
                    "failed_checks": failed_checks,
                    "message": rule.failure_message,
                }
            )
        return hits

    def _failed_checks(self, rule: RuleSpec, changed_files: list[str], prompt: str) -> list[str]:
        failed: list[str] = []
        lowered_checks = [check.lower() for check in rule.checks]
        if any("changed files should map back to the current task" in check for check in lowered_checks):
            if not changed_files:
                failed.append("changed files should map back to the current task")
        if any("avoid broad cleanup" in check for check in lowered_checks):
            if len(changed_files) > 3:
                failed.append("avoid broad cleanup when it is not required for correctness")
        if any("do not expand scope" in check for check in lowered_checks):
            if changed_files and prompt and not any(self._path_matches_prompt(path, prompt) for path in changed_files):
                failed.append("do not expand scope unless verification or architecture constraints require it")
        return failed

    def _path_matches_prompt(self, path: str, prompt: str) -> bool:
        normalized_path = path.lower().replace("\\", "/")
        prompt_tokens = {token for token in prompt.split() if len(token) >= 3}
        return any(token in normalized_path for token in prompt_tokens)
