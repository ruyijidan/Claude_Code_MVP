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
        self.assertEqual(result["critic_rule_hits"][0]["rule"], "surgical_changes")
        self.assertIn("changed files should map back to the current task", result["critic_rule_hits"][0]["failed_checks"])

    def test_rule_checks_change_critic_behavior(self) -> None:
        agent = CriticAgent(
            AgentSpec(
                name="critic",
                role="critic",
                system_prompt="critic",
                allowed_tools=[],
                input_schema={},
                output_schema={},
            ),
            [
                RuleSpec(
                    name="wide_change_guard",
                    intent="Avoid broad cleanup",
                    applies_to=["implement_feature"],
                    checks=["avoid broad cleanup when it is not required for correctness"],
                    failure_message="Too many unrelated files changed.",
                ),
                RuleSpec(
                    name="scoped_change_guard",
                    intent="Stay on scope",
                    applies_to=["implement_feature"],
                    checks=["do not expand scope unless verification or architecture constraints require it"],
                    failure_message="Changed files drift away from the task prompt.",
                ),
            ],
        )

        result = agent.run(
            {
                "request": {"feature_request": "update router behavior"},
                "task_spec": TaskSpec(
                    name="implement_feature",
                    goal="Implement feature",
                    inputs={},
                    outputs={},
                    constraints=[],
                    tools=[],
                    done_when=[],
                ),
                "changed_files": [
                    "docs/notes.md",
                    "reports/plan.md",
                    "app/tool_router.py",
                    "tests/test_tool_router.py",
                ],
                "test_result": "passed",
                "verification_errors": [],
                "gate_failures": [],
            }
        )

        self.assertIn("Too many unrelated files changed.", result["critic_issues"])
        self.assertEqual(result["critic_rule_hits"][0]["rule"], "wide_change_guard")
        self.assertNotIn("Changed files drift away from the task prompt.", result["critic_issues"])

    def test_application_verification_issues_flow_into_critic(self) -> None:
        agent = CriticAgent(
            AgentSpec(
                name="critic",
                role="critic",
                system_prompt="critic",
                allowed_tools=[],
                input_schema={},
                output_schema={},
            )
        )

        result = agent.run(
            {
                "task_spec": TaskSpec(
                    name="investigate_issue",
                    goal="Investigate",
                    inputs={},
                    outputs={},
                    constraints=[],
                    tools=[],
                    done_when=[],
                ),
                "changed_files": ["reports/investigation.md"],
                "test_result": "passed",
                "verification_errors": [],
                "application_verification": {
                    "issues": ["log artifact shows failure signal: logs/agent.log"],
                },
                "gate_failures": [],
            }
        )

        self.assertIn("log artifact shows failure signal: logs/agent.log", result["critic_issues"])

    def test_verifier_only_rule_does_not_change_critic_behavior(self) -> None:
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
                name="application_artifact_signals",
                intent="Treat artifact failures as blocking",
                applies_to=["investigate_issue"],
                checks=["application artifact failure signals must fail verification"],
                failure_message="Application artifact verification reported blocking signals.",
                enforced_by=["verifier"],
            ),
        )

        result = agent.run(
            {
                "task_spec": TaskSpec(
                    name="investigate_issue",
                    goal="Investigate",
                    inputs={},
                    outputs={},
                    constraints=[],
                    tools=[],
                    done_when=[],
                ),
                "changed_files": ["reports/investigation.md"],
                "test_result": "passed",
                "verification_errors": [],
                "application_verification": {
                    "issues": ["log artifact shows failure signal: logs/agent.log"],
                },
                "gate_failures": [],
            }
        )

        self.assertEqual(result["critic_rule_hits"], [])
        self.assertEqual(result["critic_issues"], ["log artifact shows failure signal: logs/agent.log"])


if __name__ == "__main__":
    unittest.main()
