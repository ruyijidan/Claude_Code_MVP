from __future__ import annotations

import unittest

from app.agent.verification_gates import VerificationGateRunner
from app.core.models import WorkflowSpec


class VerificationGateTests(unittest.TestCase):
    def test_post_execute_gates_pass_for_valid_feature_state(self) -> None:
        runner = VerificationGateRunner()
        workflow = WorkflowSpec(
            name="implement_feature",
            goal="Implement",
            entry_signals=[],
            required_context=[],
            steps=[],
            verification=[
                "tests must pass",
                "at least one changed file must be recorded",
                "at least one changed test file must be recorded",
                "completion contract must pass",
            ],
            stop_conditions=[],
        )

        result = runner.run_post_execute(
            {
                "task_spec": type("TaskSpecStub", (), {"name": "implement_feature"})(),
                "workflow_spec": workflow,
                "changed_files": ["sample_app/tool_router.py", "tests/test_tool_router.py"],
                "implementation_summary": "Added tool routing and coverage.",
                "test_result": "passed",
                "verification_errors": [],
            }
        )

        self.assertTrue(result["completion_check"]["passed"])
        self.assertEqual(result["gate_failures"], [])
        self.assertTrue(all(item["passed"] for item in result["gate_results"]))

    def test_post_execute_gates_report_test_and_contract_failures(self) -> None:
        runner = VerificationGateRunner()
        workflow = WorkflowSpec(
            name="fix_bug",
            goal="Fix",
            entry_signals=[],
            required_context=[],
            steps=[],
            verification=[
                "tests must pass",
                "at least one changed file must be recorded",
                "at least one changed test file must be recorded",
                "completion contract must pass",
            ],
            stop_conditions=[],
        )

        result = runner.run_post_execute(
            {
                "task_spec": type("TaskSpecStub", (), {"name": "fix_bug"})(),
                "workflow_spec": workflow,
                "changed_files": ["sample_app/calculator.py"],
                "implementation_summary": "Updated the calculator logic.",
                "test_result": "failed",
                "verification_errors": [],
            }
        )

        self.assertFalse(result["completion_check"]["passed"])
        self.assertIn("tests did not pass", result["gate_failures"])
        self.assertIn("fix_bug requires at least one changed test file", result["gate_failures"])

    def test_workflow_verification_can_skip_test_file_gate(self) -> None:
        runner = VerificationGateRunner()
        workflow = WorkflowSpec(
            name="investigate_issue",
            goal="Investigate",
            entry_signals=[],
            required_context=[],
            steps=[],
            verification=[
                "tests must pass",
                "at least one changed file must be recorded",
                "completion contract must pass",
            ],
            stop_conditions=[],
        )

        result = runner.run_post_execute(
            {
                "task_spec": type("TaskSpecStub", (), {"name": "investigate_issue"})(),
                "workflow_spec": workflow,
                "changed_files": ["reports/investigation.md"],
                "implementation_summary": "Generated an investigation report.",
                "test_result": "passed",
                "verification_errors": [],
            }
        )

        gate_names = {item["name"] for item in result["gate_results"]}
        self.assertNotIn("changed_test_file_recorded", gate_names)
        self.assertTrue(result["completion_check"]["passed"])


if __name__ == "__main__":
    unittest.main()
