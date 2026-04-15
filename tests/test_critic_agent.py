from __future__ import annotations

import unittest

from app.agents.critic_agent import CriticAgent
from app.core.models import AgentSpec, RuleSpec, TaskSpec


class CriticAgentTests(unittest.TestCase):
    def test_rule_adds_issue_when_no_changed_files_exist(self) -> None:
        agent = CriticAgent(
            AgentSpec(
                name="critic",
                role="critic",
                system_prompt="critic",
                allowed_tools=[],
                input_schema={},
                output_schema={},
            ),
            RuleSpec(
                name="surgical_changes",
                intent="Prefer small changes",
                applies_to=["implement_feature"],
                checks=["changed files should map back to the current task"],
                failure_message="The proposed change set is broader than the task requires.",
            ),
        )

        result = agent.run(
            {
                "task_spec": TaskSpec(
                    name="implement_feature",
                    goal="Implement feature",
                    inputs={},
                    outputs={},
                    constraints=[],
                    tools=[],
                    done_when=[],
                ),
                "changed_files": [],
                "test_result": "passed",
                "verification_errors": [],
                "gate_failures": [],
            }
        )

        self.assertIn("The proposed change set is broader than the task requires.", result["critic_issues"])


if __name__ == "__main__":
    unittest.main()
