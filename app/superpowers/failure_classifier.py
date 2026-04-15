from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from app.core.task_templates import build_task_artifacts


@dataclass(slots=True)
class FailureSignal:
    kind: str
    message: str
    retryable: bool

    def to_dict(self) -> dict:
        return asdict(self)


class FailureClassifier:
    def classify(self, state: dict, issues: list[str]) -> list[FailureSignal]:
        signals: list[FailureSignal] = []
        changed_files = state.get("changed_files", [])
        missing_test_file = self._is_expected_test_file_missing(state)

        if not changed_files:
            signals.append(
                FailureSignal(
                    kind="no_effect_change",
                    message="no changed files were recorded",
                    retryable=True,
                )
            )

        if missing_test_file:
            signals.append(
                FailureSignal(
                    kind="missing_tests",
                    message="expected task test file is missing",
                    retryable=True,
                )
            )

        for issue in issues:
            lowered = issue.lower()
            if "changed test file" in lowered or "missing_tests" in lowered:
                signals.append(
                    FailureSignal(
                        kind="missing_tests",
                        message=issue,
                        retryable=True,
                    )
                )
                continue

            if "architecture" in lowered or "boundary" in lowered:
                signals.append(
                    FailureSignal(
                        kind="architecture_violation",
                        message=issue,
                        retryable=False,
                    )
                )
                continue

            if "tests_failed" in lowered or "tests did not pass" in lowered or "test" in lowered:
                signals.append(
                    FailureSignal(
                        kind="test_failure",
                        message=issue,
                        retryable=True,
                    )
                )

        return self._dedupe(signals)

    def _is_expected_test_file_missing(self, state: dict) -> bool:
        task_spec = state.get("task_spec")
        repo_path = state.get("repo_path")
        if task_spec is None or repo_path is None:
            return False
        artifacts = build_task_artifacts(task_spec.name)
        test_path = artifacts.get("test_path")
        if not test_path:
            return False
        return not (Path(repo_path) / test_path).exists()

    def _dedupe(self, signals: list[FailureSignal]) -> list[FailureSignal]:
        unique: list[FailureSignal] = []
        seen: set[tuple[str, str]] = set()
        for signal in signals:
            key = (signal.kind, signal.message)
            if key in seen:
                continue
            seen.add(key)
            unique.append(signal)
        return unique
