from __future__ import annotations

from dataclasses import asdict, dataclass

from app.superpowers.failure_classifier import FailureSignal


@dataclass(slots=True)
class RepairDecision:
    action: str
    retry_allowed: bool
    reason: str

    def to_dict(self) -> dict:
        return asdict(self)


class RepairPolicy:
    def __init__(self, max_test_failure_attempts: int = 2) -> None:
        self.max_test_failure_attempts = max_test_failure_attempts

    def decide(self, attempt: int, failure_signals: list[FailureSignal]) -> RepairDecision:
        if not failure_signals:
            return RepairDecision(
                action="none",
                retry_allowed=False,
                reason="no failure signals detected",
            )

        kinds = {signal.kind for signal in failure_signals}

        if "architecture_violation" in kinds:
            return RepairDecision(
                action="stop",
                retry_allowed=False,
                reason="architecture violations stop repair by default",
            )

        if "missing_tests" in kinds:
            return RepairDecision(
                action="add_missing_tests",
                retry_allowed=True,
                reason="missing tests can be repaired deterministically",
            )

        if "no_effect_change" in kinds:
            return RepairDecision(
                action="retry_with_existing_changes",
                retry_allowed=attempt < 2,
                reason="retry once when no effective change was recorded",
            )

        if "test_failure" in kinds:
            return RepairDecision(
                action="retry_tests",
                retry_allowed=attempt < self.max_test_failure_attempts,
                reason="bounded retries are allowed for test failures",
            )

        return RepairDecision(
            action="stop",
            retry_allowed=False,
            reason="no repair policy matched the current failure signals",
        )
