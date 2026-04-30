from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.agents.verifier_agent import VerifierAgent
from app.core.models import AgentSpec, TaskSpec
from app.runtime.local_runtime import LocalRuntimeAdapter


class VerifierAgentTests(unittest.TestCase):
    def _agent(self) -> VerifierAgent:
        return VerifierAgent(
            AgentSpec(
                name="verifier",
                role="verifier",
                system_prompt="verify",
                allowed_tools=["test_tool"],
                input_schema={},
                output_schema={},
            ),
            LocalRuntimeAdapter(),
        )

    def _task_spec(self) -> TaskSpec:
        return TaskSpec(
            name="investigate_issue",
            goal="Investigate",
            inputs={},
            outputs={},
            constraints=[],
            tools=[],
            done_when=[],
        )

    def test_verifier_reports_application_findings_and_log_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            (repo_path / "tests").mkdir()
            (repo_path / "tests" / "test_ok.py").write_text(
                "import unittest\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            result = self._agent().run(
                {
                    "repo_path": repo_path,
                    "task_spec": self._task_spec(),
                    "repo_context": {
                        "application_legibility": {
                            "artifact_summaries": [
                                {"kind": "preview", "path": "examples/web/index.html", "summary": "<html>ok</html>"},
                                {"kind": "log", "path": "logs/agent.log", "summary": "Traceback: failure"},
                                {"kind": "metric", "path": "reports/coverage.json", "summary": '{"line_rate": 0.90}'},
                            ]
                        }
                    },
                }
            )

        self.assertEqual(result["test_result"], "passed")
        self.assertTrue(result["application_verification"]["available"])
        self.assertIn("preview", result["application_verification"]["checked_kinds"])
        self.assertIn("log", result["application_verification"]["checked_kinds"])
        self.assertIn("metric", result["application_verification"]["checked_kinds"])
        self.assertIn("log artifact shows failure signal: logs/agent.log", result["application_verification"]["issues"])

    def test_verifier_reports_metric_issue_for_zero_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            (repo_path / "tests").mkdir()
            (repo_path / "tests" / "test_ok.py").write_text(
                "import unittest\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            result = self._agent().run(
                {
                    "repo_path": repo_path,
                    "task_spec": self._task_spec(),
                    "repo_context": {
                        "application_legibility": {
                            "artifact_summaries": [
                                {"kind": "metric", "path": "reports/coverage.json", "summary": '{"line_rate": 0}'},
                            ]
                        }
                    },
                }
            )

        self.assertIn("metric artifact shows zero line coverage: reports/coverage.json", result["application_verification"]["issues"])


if __name__ == "__main__":
    unittest.main()
