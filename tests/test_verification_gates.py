from __future__ import annotations

import unittest

from app.agent.verification_gates import VerificationGateRunner


class VerificationGateTests(unittest.TestCase):
    def test_post_execute_gates_pass_for_valid_feature_state(self) -> None:
        runner = VerificationGateRunner()

        result = runner.run_post_execute(
            {
                "task_spec": type("TaskSpecStub", (), {"name": "implement_feature"})(),
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

        result = runner.run_post_execute(
            {
                "task_spec": type("TaskSpecStub", (), {"name": "fix_bug"})(),
                "changed_files": ["sample_app/calculator.py"],
                "implementation_summary": "Updated the calculator logic.",
                "test_result": "failed",
                "verification_errors": [],
            }
        )

        self.assertFalse(result["completion_check"]["passed"])
        self.assertIn("tests did not pass", result["gate_failures"])
        self.assertIn("fix_bug requires at least one changed test file", result["gate_failures"])


if __name__ == "__main__":
    unittest.main()
