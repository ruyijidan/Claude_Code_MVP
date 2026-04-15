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
        required_checks = list(workflow.verification) if workflow is not None else ["changed files recorded", "summary recorded"]

        if not isinstance(changed_files, list) or not changed_files:
            reasons.append("expected at least one changed file")

        if not isinstance(summary, str) or not summary.strip():
            reasons.append("expected a non-empty summary")

        verification_text = " ".join(required_checks).lower()
        if workflow is None and task_type in {"fix_bug", "write_tests", "implement_feature"}:
            verification_text = f"{verification_text} changed test file"
        if "changed test file" in verification_text and not self._has_test_file(changed_files):
            reasons.append(f"{task_type} requires at least one changed test file")

        return CompletionCheck(
            passed=not reasons,
            reasons=reasons,
            required_checks=required_checks,
        )

    def _has_test_file(self, changed_files: list[str]) -> bool:
        for path in changed_files:
            normalized = path.replace("\\", "/")
            if normalized.startswith("tests/") or "/tests/" in normalized:
                return True
            if normalized.rsplit("/", maxsplit=1)[-1].startswith("test_"):
                return True
        return False
