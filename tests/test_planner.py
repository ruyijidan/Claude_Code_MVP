from __future__ import annotations

import unittest
from pathlib import Path

from app.agent.planner import LightweightPlanner
from app.core.spec_loader import SpecLoader
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

    def test_application_legibility_adds_workflow_step(self) -> None:
        planner = LightweightPlanner()
        workflow = WorkflowSpec(
            name="custom_workflow",
            goal="Test",
            entry_signals=[],
            required_context=["AGENTS.md"],
            clarification_fields=[],
            steps=["inspect custom surface"],
            verification=["tests must pass"],
            stop_conditions=[],
        )

        plan = planner.build_plan(
            "inspect preview output",
            {
                "context_budget": {"max_candidate_files": 12},
                "application_legibility": {
                    "preview_targets": ["examples/web/index.html"],
                    "log_files": ["logs/agent.log"],
                    "metric_files": [],
                },
            },
            "investigate_issue",
            workflow,
        )

        self.assertEqual(plan[1]["id"], "workflow_legibility")
        self.assertIn("preview targets", plan[1]["artifact_kinds"])
        self.assertIn("log files", plan[1]["artifact_kinds"])
        self.assertEqual(plan[2]["workflow"], "custom_workflow")

    def test_memory_hits_add_memory_step_and_focus_paths(self) -> None:
        planner = LightweightPlanner()
        workflow = WorkflowSpec(
            name="custom_workflow",
            goal="Test",
            entry_signals=[],
            required_context=["AGENTS.md", "likely_relevant_files"],
            clarification_fields=[],
            steps=["inspect custom surface"],
            verification=["tests must pass"],
            stop_conditions=[],
        )

        plan = planner.build_plan(
            "write tests",
            {
                "context_budget": {"max_candidate_files": 12},
                "likely_relevant_files": ["src/current.py"],
                "memory_context_paths": ["planner.py", "tests/test_planner.py"],
                "memory_hits": [{"task": "write_tests", "request_prompt": "write tests for planner.py", "score": 7}],
            },
            "write_tests",
            workflow,
        )

        self.assertEqual(plan[0]["id"], "workflow_context")
        self.assertIn("planner.py", plan[0]["focused_paths"])
        self.assertIn("prioritize planner.py", plan[0]["description"])
        self.assertEqual(plan[1]["id"], "workflow_memory")
        self.assertEqual(plan[1]["memory_context_paths"][0], "planner.py")

    def test_planner_uses_workflow_assets_for_task_type_and_name_resolution(self) -> None:
        planner = LightweightPlanner()
        root = Path(__file__).resolve().parents[1] / "specs"
        workflows = SpecLoader(root).load_workflows()

        task_type = planner.infer_task_type("fix the failing router test", workflows)
        workflow_name = planner.workflow_name_for_task_type(task_type, workflows)

        self.assertEqual(task_type, "fix_bug")
        self.assertEqual(workflow_name, "bugfix")


if __name__ == "__main__":
    unittest.main()
