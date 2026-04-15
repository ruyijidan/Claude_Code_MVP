from __future__ import annotations

from dataclasses import asdict, dataclass

from app.agent.completion_contracts import CompletionContractRegistry


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
        completion_check = self.contracts.evaluate(task_type, state)
        gate_results = [
            self._tests_passed_gate(state),
            self._architecture_gate(state),
            self._completion_gate(completion_check),
        ]
        return {
            "completion_check": completion_check.to_dict(),
            "gate_results": [gate.to_dict() for gate in gate_results],
            "gate_failures": [gate.message for gate in gate_results if not gate.passed],
        }

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
