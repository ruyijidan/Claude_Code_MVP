from __future__ import annotations

from dataclasses import asdict, dataclass

from app.agent.completion_contracts import CompletionContractRegistry
from app.core.models import WorkflowSpec


@dataclass(slots=True)
class GateResult:
    name: str
    passed: bool
    severity: str
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


class VerificationGateRunner:
    def __init__(self, contracts: CompletionContractRegistry | None = None) -> None:
        self.contracts = contracts or CompletionContractRegistry()

    def run_post_execute(self, state: dict) -> dict:
        task_spec = state.get("task_spec")
        task_type = task_spec.name if task_spec is not None else "implement_feature"
        workflow = state.get("workflow_spec")
        completion_check = self.contracts.evaluate(task_type, state, workflow)
        gate_results = self._workflow_verification_gates(state, workflow)
        gate_results.append(self._architecture_gate(state))
        gate_results.append(self._completion_gate(completion_check))
        return {
            "completion_check": completion_check.to_dict(),
            "gate_results": [gate.to_dict() for gate in gate_results],
            "gate_failures": [gate.message for gate in gate_results if not gate.passed],
        }

    def _workflow_verification_gates(self, state: dict, workflow: WorkflowSpec | None) -> list[GateResult]:
        verification_items = list(workflow.verification) if workflow is not None else ["tests must pass", "completion contract must pass"]
        gates: list[GateResult] = []
        changed_files = state.get("changed_files", [])

        for item in verification_items:
            lowered = item.lower()
            if "tests must pass" in lowered:
                gates.append(self._tests_passed_gate(state))
                continue
            if "changed test file" in lowered:
                passed = self._has_test_file(changed_files)
                gates.append(
                    GateResult(
                        name="changed_test_file_recorded",
                        passed=passed,
                        severity="error",
                        message="changed test file recorded" if passed else "no changed test file was recorded",
                    )
                )
                continue
            if "changed file" in lowered:
                passed = isinstance(changed_files, list) and bool(changed_files)
                gates.append(
                    GateResult(
                        name="changed_files_recorded",
                        passed=passed,
                        severity="error",
                        message="changed files recorded" if passed else "no changed files were recorded",
                    )
                )
        return gates

    def _tests_passed_gate(self, state: dict) -> GateResult:
        passed = state.get("test_result") == "passed"
        return GateResult(
            name="tests_passed",
            passed=passed,
            severity="error",
            message="tests did not pass" if not passed else "tests passed",
        )

    def _architecture_gate(self, state: dict) -> GateResult:
        errors = state.get("verification_errors", [])
        architecture_errors = [
            error
            for error in errors
            if "architecture" in error.lower() or "boundary" in error.lower()
        ]
        passed = not architecture_errors
        return GateResult(
            name="no_architecture_violation",
            passed=passed,
            severity="error",
            message="; ".join(architecture_errors) if architecture_errors else "no architecture violation detected",
        )

    def _completion_gate(self, completion_check) -> GateResult:
        passed = completion_check.passed
        return GateResult(
            name="completion_contract",
            passed=passed,
            severity="error",
            message="; ".join(completion_check.reasons) if not passed else "completion contract passed",
        )

    def _has_test_file(self, changed_files: list[str]) -> bool:
        for path in changed_files:
            normalized = path.replace("\\", "/")
            if normalized.startswith("tests/") or "/tests/" in normalized:
                return True
            if normalized.rsplit("/", maxsplit=1)[-1].startswith("test_"):
                return True
        return False
