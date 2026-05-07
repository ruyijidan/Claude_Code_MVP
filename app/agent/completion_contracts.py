from __future__ import annotations

from dataclasses import asdict, dataclass

from app.core.models import WorkflowSpec


@dataclass(slots=True)
class CompletionCheck:
    passed: bool
    reasons: list[str]
    required_checks: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


class CompletionContractRegistry:
    def evaluate(self, task_type: str, state: dict, workflow: WorkflowSpec | None = None) -> CompletionCheck:
        changed_files = state.get("changed_files", [])
        summary = state.get("implementation_summary") or state.get("summary")
        reasons: list[str] = []
        required_checks = self._required_checks(workflow)

        if not isinstance(changed_files, list) or not changed_files:
            reasons.append("expected at least one changed file")

        if not isinstance(summary, str) or not summary.strip():
            reasons.append("expected a non-empty summary")

        if self._requires_changed_test_file(task_type, workflow) and not self._has_test_file(changed_files):
            reasons.append(f"{task_type} requires at least one changed test file")

        return CompletionCheck(
            passed=not reasons,
            reasons=reasons,
            required_checks=required_checks,
        )

    def _required_checks(self, workflow: WorkflowSpec | None) -> list[str]:
        if workflow is None:
            return ["changed files recorded", "summary recorded"]
        if workflow.verification_gates:
            return [gate.name for gate in workflow.verification_gates if gate.enabled]
        return list(workflow.verification)

    def _requires_changed_test_file(self, task_type: str, workflow: WorkflowSpec | None) -> bool:
        if workflow is None:
            return task_type in {"fix_bug", "write_tests", "implement_feature"}
        if workflow.verification_gates:
            return any(gate.enabled and gate.name == "changed_test_file_recorded" for gate in workflow.verification_gates)
        verification_text = " ".join(workflow.verification).lower()
        return "changed test file" in verification_text

    def _has_test_file(self, changed_files: list[str]) -> bool:
        for path in changed_files:
            normalized = path.replace("\\", "/")
            if normalized.startswith("tests/") or "/tests/" in normalized:
                return True
            if normalized.rsplit("/", maxsplit=1)[-1].startswith("test_"):
                return True
        return False
