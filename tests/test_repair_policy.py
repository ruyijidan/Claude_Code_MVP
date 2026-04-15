from __future__ import annotations

import unittest

from app.core.models import WorkflowSpec
from app.superpowers.failure_classifier import FailureSignal
from app.superpowers.repair_policy import RepairPolicy


class RepairPolicyTests(unittest.TestCase):
    def test_stops_on_architecture_violation(self) -> None:
        policy = RepairPolicy()

        decision = policy.decide(
            1,
            [FailureSignal(kind="architecture_violation", message="boundary violation", retryable=False)],
        )

        self.assertEqual(decision.action, "stop")
        self.assertFalse(decision.retry_allowed)

    def test_repairs_missing_tests(self) -> None:
        policy = RepairPolicy()

        decision = policy.decide(
            1,
            [FailureSignal(kind="missing_tests", message="missing test file", retryable=True)],
        )

        self.assertEqual(decision.action, "add_missing_tests")
        self.assertTrue(decision.retry_allowed)

    def test_bounds_test_failure_retries(self) -> None:
        policy = RepairPolicy(max_test_failure_attempts=2)

        first = policy.decide(
            1,
            [FailureSignal(kind="test_failure", message="tests_failed", retryable=True)],
        )
        second = policy.decide(
            2,
            [FailureSignal(kind="test_failure", message="tests_failed", retryable=True)],
        )

        self.assertTrue(first.retry_allowed)
        self.assertFalse(second.retry_allowed)

    def test_workflow_stop_conditions_are_accepted_by_policy_interface(self) -> None:
        policy = RepairPolicy(max_test_failure_attempts=2)
        workflow = WorkflowSpec(
            name="bugfix",
            goal="Fix",
            entry_signals=[],
            required_context=[],
            steps=[],
            verification=[],
            stop_conditions=[
                "architecture violation detected",
                "repair policy denies retry",
                "maximum retry budget reached",
            ],
        )

        decision = policy.decide(
            1,
            [FailureSignal(kind="architecture_violation", message="boundary violation", retryable=False)],
            workflow,
        )

        self.assertEqual(decision.action, "stop")
        self.assertFalse(decision.retry_allowed)


if __name__ == "__main__":
    unittest.main()
