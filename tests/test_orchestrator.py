from __future__ import annotations

import unittest

from app.agent.orchestrator import AgentOrchestrator
from app.core.models import AgentSpec


class OrchestratorTests(unittest.TestCase):
    def test_isolated_state_respects_declared_inputs_and_shared_runtime_keys(self) -> None:
        orchestrator = AgentOrchestrator()
        spec = AgentSpec(
            name="coder",
            role="coder",
            system_prompt="code",
            allowed_tools=["file_tool"],
            input_schema={"plan": "list"},
            output_schema={"changed_files": "list"},
        )

        isolated = orchestrator.isolated_state(
            spec,
            {
                "repo_path": "/tmp/repo",
                "plan": [{"id": "x"}],
                "repo_context": {"memory_hits": []},
                "changed_files": ["x.py"],
            },
        )

        self.assertIn("repo_path", isolated)
        self.assertIn("plan", isolated)
        self.assertIn("repo_context", isolated)
        self.assertIn("changed_files", isolated)

    def test_record_transition_captures_contract_and_outputs(self) -> None:
        orchestrator = AgentOrchestrator()
        spec = AgentSpec(
            name="verifier",
            role="verifier",
            system_prompt="verify",
            allowed_tools=["test_tool"],
            input_schema={"changed_files": "list"},
            output_schema={"test_result": "string"},
        )
        state_before = {"changed_files": ["a.py"], "repo_path": "/tmp/repo"}
        result = {"test_result": "passed", "summary": "ok"}

        orchestrator.record_transition(spec, state_before, result, status="completed", next_agent="critic")

        history = orchestrator.history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["agent"], "verifier")
        self.assertEqual(history[0]["allowed_tools"], ["test_tool"])
        self.assertIn("changed_files", history[0]["declared_input_keys"])
        self.assertIn("test_result", history[0]["observed_output_keys"])
        self.assertEqual(history[0]["next_agent"], "critic")


if __name__ == "__main__":
    unittest.main()
