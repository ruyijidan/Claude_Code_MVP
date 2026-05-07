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
        permission_rules = loader.load_permission_rules()
        tool = loader.load_tool("test_tool")
        reader = loader.load_reader("browser_preview")
        template = loader.load_template("plan-template")

        self.assertEqual(workflow.name, "bugfix")
        self.assertIn("target", workflow.clarification_fields)
        self.assertIn("tests must pass", workflow.verification)
        self.assertIn("completion_contract", {gate.name for gate in workflow.verification_gates})
        self.assertEqual(rule.name, "surgical_changes")
        self.assertEqual(permission_rules.name, "permission_rules_v1")
        self.assertEqual(tool.name, "test_tool")
        self.assertEqual(reader.artifact_kind, "preview")
        self.assertIn(".claude-code", permission_rules.runtime_artifact_dirs)
        self.assertIn("smallest relevant change", rule.intent)
        self.assertIn("## Goal", template)

    def test_load_rules_returns_non_permission_rule_assets(self) -> None:
        root = Path(__file__).resolve().parents[1] / "specs"
        loader = SpecLoader(root)

        rules = loader.load_rules()

        self.assertTrue(rules)
        self.assertTrue(all(rule.name != "permission_rules_v1" for rule in rules))
        self.assertIn("surgical_changes", {rule.name for rule in rules})
        self.assertIn("application_artifact_signals", {rule.name for rule in rules})

    def test_load_additional_workflows(self) -> None:
        root = Path(__file__).resolve().parents[1] / "specs"
        loader = SpecLoader(root)

        write_tests = loader.load_workflow("write-tests")
        investigate = loader.load_workflow("investigate-issue")

        self.assertEqual(write_tests.name, "write_tests")
        self.assertEqual(investigate.name, "investigate_issue")

    def test_load_tool_and_reader_collections(self) -> None:
        root = Path(__file__).resolve().parents[1] / "specs"
        loader = SpecLoader(root)

        tools = loader.load_tools()
        readers = loader.load_readers()

        self.assertIn("file_tool", {tool.name for tool in tools})
        self.assertIn("test_tool", {tool.name for tool in tools})
        self.assertIn("browser_preview", {reader.name for reader in readers})
        self.assertIn("log_artifact", {reader.name for reader in readers})


if __name__ == "__main__":
    unittest.main()
