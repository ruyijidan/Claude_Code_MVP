from __future__ import annotations

import unittest

from app.agent.planner import LightweightPlanner
from app.core.models import WorkflowSpec


class PlannerTests(unittest.TestCase):
    def test_workflow_assets_shape_plan_context_and_clarification_steps(self) -> None:
        planner = LightweightPlanner()
        workflow = WorkflowSpec(
            name="custom_workflow",
            goal="Test",
            entry_signals=[],
            required_context=["AGENTS.md", "likely_relevant_files", "test_targets"],
            clarification_fields=["target", "success_criteria"],
            steps=["inspect custom surface", "run custom verification"],
            verification=["tests must pass"],
            stop_conditions=[],
        )

        plan = planner.build_plan(
            "fix router",
            {"context_budget": {"max_candidate_files": 12}},
            "fix_bug",
            workflow,
        )

        self.assertEqual(plan[0]["id"], "workflow_context")
        self.assertIn("AGENTS.md", plan[0]["description"])
        self.assertEqual(plan[1]["id"], "workflow_clarification")
        self.assertIn("target", plan[1]["clarification_fields"])
        self.assertEqual(plan[2]["workflow"], "custom_workflow")
        self.assertIn("tests must pass", plan[2]["verification_targets"])


if __name__ == "__main__":
    unittest.main()
