from __future__ import annotations

from dataclasses import asdict, dataclass

from app.agent.completion_contracts import CompletionContractRegistry
from app.core.models import VerificationGateSpec, WorkflowSpec


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
        gate_results = self._workflow_verification_gates(state, workflow, completion_check)
        gate_results.extend(self._application_legibility_gates(state))
        gate_results.append(self._architecture_gate(state))
        return {
            "completion_check": completion_check.to_dict(),
            "gate_results": [gate.to_dict() for gate in gate_results],
            "gate_failures": [gate.message for gate in gate_results if not gate.passed],
        }

    def _workflow_verification_gates(
        self,
        state: dict,
        workflow: WorkflowSpec | None,
        completion_check,
    ) -> list[GateResult]:
        gate_specs = self._resolve_workflow_gate_specs(workflow)
        gates: list[GateResult] = []
        changed_files = state.get("changed_files", [])

        for gate_spec in gate_specs:
            gate = self._evaluate_workflow_gate(gate_spec, state, changed_files, completion_check)
            if gate is not None:
                gates.append(gate)
        return gates

    def _resolve_workflow_gate_specs(self, workflow: WorkflowSpec | None) -> list[VerificationGateSpec]:
        if workflow is None:
            return [
                VerificationGateSpec(name="tests_passed"),
                VerificationGateSpec(name="completion_contract"),
            ]
        if workflow.verification_gates:
            return [gate for gate in workflow.verification_gates if gate.enabled]
        return self._legacy_gate_specs(workflow.verification)

    def _legacy_gate_specs(self, verification_items: list[str]) -> list[VerificationGateSpec]:
        gate_specs: list[VerificationGateSpec] = []
        for item in verification_items:
            lowered = item.lower()
            if "tests must pass" in lowered:
                gate_specs.append(VerificationGateSpec(name="tests_passed"))
                continue
            if "changed test file" in lowered:
                gate_specs.append(VerificationGateSpec(name="changed_test_file_recorded"))
                continue
            if "changed file" in lowered:
                gate_specs.append(VerificationGateSpec(name="changed_files_recorded"))
                continue
            if "completion contract must pass" in lowered:
                gate_specs.append(VerificationGateSpec(name="completion_contract"))
        return gate_specs

    def _evaluate_workflow_gate(
        self,
        gate_spec: VerificationGateSpec,
        state: dict,
        changed_files: list[str],
        completion_check,
    ) -> GateResult | None:
        if gate_spec.name == "tests_passed":
            return self._tests_passed_gate(state, severity=gate_spec.severity)
        if gate_spec.name == "changed_test_file_recorded":
            passed = self._has_test_file(changed_files)
            return GateResult(
                name="changed_test_file_recorded",
                passed=passed,
                severity=gate_spec.severity,
                message="changed test file recorded" if passed else "no changed test file was recorded",
            )
        if gate_spec.name == "changed_files_recorded":
            passed = isinstance(changed_files, list) and bool(changed_files)
            return GateResult(
                name="changed_files_recorded",
                passed=passed,
                severity=gate_spec.severity,
                message="changed files recorded" if passed else "no changed files were recorded",
            )
        if gate_spec.name == "completion_contract":
            return self._completion_gate(completion_check, severity=gate_spec.severity)
        return GateResult(
            name=gate_spec.name,
            passed=False,
            severity=gate_spec.severity,
            message=f"unknown workflow verification gate: {gate_spec.name}",
        )

    def _tests_passed_gate(self, state: dict, *, severity: str = "error") -> GateResult:
        passed = state.get("test_result") == "passed"
        return GateResult(
            name="tests_passed",
            passed=passed,
            severity=severity,
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

    def _completion_gate(self, completion_check, *, severity: str = "error") -> GateResult:
        passed = completion_check.passed
        return GateResult(
            name="completion_contract",
            passed=passed,
            severity=severity,
            message="; ".join(completion_check.reasons) if not passed else "completion contract passed",
        )

    def _application_legibility_gates(self, state: dict) -> list[GateResult]:
        repo_context = state.get("repo_context", {})
        legibility = repo_context.get("application_legibility", {})
        artifact_summaries = legibility.get("artifact_summaries", [])
        if not isinstance(artifact_summaries, list):
            artifact_summaries = []

        gates: list[GateResult] = []
        gates.extend(self._artifact_summary_gate(legibility, artifact_summaries, "preview", "preview_targets"))
        gates.extend(self._artifact_summary_gate(legibility, artifact_summaries, "log", "log_files"))
        gates.extend(self._artifact_summary_gate(legibility, artifact_summaries, "metric", "metric_files"))
        return gates

    def _artifact_summary_gate(
        self,
        legibility: dict,
        artifact_summaries: list[dict],
        kind: str,
        path_key: str,
    ) -> list[GateResult]:
        artifact_paths = legibility.get(path_key, [])
        if not artifact_paths:
            return []
        summarized_paths = {
            item.get("path")
            for item in artifact_summaries
            if isinstance(item, dict) and item.get("kind") == kind and item.get("path")
        }
        missing_paths = [path for path in artifact_paths if path not in summarized_paths]
        passed = not missing_paths
        return [
            GateResult(
                name=f"{kind}_artifacts_summarized",
                passed=passed,
                severity="error",
                message=(
                    f"{kind} artifacts summarized"
                    if passed
                    else f"missing {kind} artifact summaries: {', '.join(missing_paths)}"
                ),
            )
        ]

    def _has_test_file(self, changed_files: list[str]) -> bool:
        for path in changed_files:
            normalized = path.replace("\\", "/")
            if normalized.startswith("tests/") or "/tests/" in normalized:
                return True
            if normalized.rsplit("/", maxsplit=1)[-1].startswith("test_"):
                return True
        return False
