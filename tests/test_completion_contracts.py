from __future__ import annotations

import unittest

from app.agent.completion_contracts import CompletionContractRegistry
from app.core.models import VerificationGateSpec, WorkflowSpec


class CompletionContractTests(unittest.TestCase):
    def test_fix_bug_requires_changed_test_file(self) -> None:
        registry = CompletionContractRegistry()

        failed = registry.evaluate(
            "fix_bug",
            {
                "changed_files": ["sample_app/calculator.py"],
                "implementation_summary": "Updated the calculator logic.",
            },
        )
        passed = registry.evaluate(
            "fix_bug",
            {
                "changed_files": ["sample_app/calculator.py", "tests/test_calculator.py"],
                "implementation_summary": "Updated the calculator logic and regression coverage.",
            },
        )

        self.assertFalse(failed.passed)
        self.assertIn("requires at least one changed test file", failed.reasons[0])
        self.assertTrue(passed.passed)

    def test_generic_contract_requires_changes_and_summary(self) -> None:
        registry = CompletionContractRegistry()

        check = registry.evaluate("investigate_issue", {"changed_files": [], "summary": ""})

        self.assertFalse(check.passed)
        self.assertEqual(
            check.reasons,
            ["expected at least one changed file", "expected a non-empty summary"],
        )

    def test_workflow_verification_controls_test_file_requirement(self) -> None:
        registry = CompletionContractRegistry()
        workflow = WorkflowSpec(
            name="investigate_issue",
            goal="Investigate",
            entry_signals=[],
            required_context=[],
            steps=[],
            verification=["tests must pass", "at least one changed file must be recorded", "completion contract must pass"],
            stop_conditions=[],
        )

        check = registry.evaluate(
            "investigate_issue",
            {
                "changed_files": ["reports/investigation.md"],
                "implementation_summary": "Generated an investigation report.",
            },
            workflow,
        )

        self.assertTrue(check.passed)

    def test_structured_workflow_gates_control_test_file_requirement(self) -> None:
        registry = CompletionContractRegistry()
        workflow = WorkflowSpec(
            name="implement_feature",
            goal="Implement",
            entry_signals=[],
            required_context=[],
            steps=[],
            verification=["tests must pass", "at least one changed test file must be recorded", "completion contract must pass"],
            verification_gates=[
                VerificationGateSpec(name="changed_files_recorded"),
                VerificationGateSpec(name="completion_contract"),
            ],
            stop_conditions=[],
        )

        check = registry.evaluate(
            "implement_feature",
            {
                "changed_files": ["app/runtime/local_runtime.py"],
                "implementation_summary": "Added a focused feature change.",
            },
            workflow,
        )

        self.assertTrue(check.passed)

    def test_long_task_game_workflow_does_not_require_test_file(self) -> None:
        registry = CompletionContractRegistry()
        workflow = WorkflowSpec(
            name="long_task_game",
            goal="Improve a browser mini-game",
            entry_signals=[],
            required_context=[],
            steps=[],
            verification=["tests must pass", "at least one changed file must be recorded", "completion_contract"],
            verification_gates=[
                VerificationGateSpec(name="tests_passed"),
                VerificationGateSpec(name="changed_files_recorded"),
                VerificationGateSpec(name="completion_contract"),
            ],
            stop_conditions=[],
        )

        check = registry.evaluate(
            "long_task_game",
            {
                "changed_files": ["examples/halo-drift/game.js"],
                "implementation_summary": "Improved the browser mini-game.",
            },
            workflow,
        )

        self.assertTrue(check.passed)


if __name__ == "__main__":
    unittest.main()
