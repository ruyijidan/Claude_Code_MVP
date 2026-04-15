from __future__ import annotations

import unittest
from pathlib import Path

from app.core.spec_loader import SpecLoader


class SpecLoaderTests(unittest.TestCase):
    def test_load_task(self) -> None:
        root = Path(__file__).resolve().parents[1] / "specs"
        loader = SpecLoader(root)
        task = loader.load_task("implement_feature")
        self.assertEqual(task.name, "implement_feature")
        self.assertIn("feature_request", task.inputs)

    def test_load_workflow_rule_and_template(self) -> None:
        root = Path(__file__).resolve().parents[1] / "specs"
        loader = SpecLoader(root)

        workflow = loader.load_workflow("bugfix")
        rule = loader.load_rule("surgical-changes")
        template = loader.load_template("plan-template")

        self.assertEqual(workflow.name, "bugfix")
        self.assertIn("tests must pass", workflow.verification)
        self.assertEqual(rule.name, "surgical_changes")
        self.assertIn("smallest relevant change", rule.intent)
        self.assertIn("## Goal", template)

    def test_load_additional_workflows(self) -> None:
        root = Path(__file__).resolve().parents[1] / "specs"
        loader = SpecLoader(root)

        write_tests = loader.load_workflow("write-tests")
        investigate = loader.load_workflow("investigate-issue")

        self.assertEqual(write_tests.name, "write_tests")
        self.assertEqual(investigate.name, "investigate_issue")


if __name__ == "__main__":
    unittest.main()
