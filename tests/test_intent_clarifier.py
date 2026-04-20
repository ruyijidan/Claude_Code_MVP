from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.agent.intent_clarifier import IntentClarifier
from app.core.spec_loader import SpecLoader


class IntentClarifierTests(unittest.TestCase):
    def setUp(self) -> None:
        spec_root = Path(__file__).resolve().parents[1] / "specs"
        self.clarifier = IntentClarifier(SpecLoader(spec_root))

    def test_ready_for_clear_bugfix_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = self.clarifier.clarify("fix failing tests", Path(tmp_dir))
        self.assertEqual(result.status, "ready")
        self.assertEqual(result.inferred_task_type, "fix_bug")
        self.assertEqual(result.missing_constraints, [])

    def test_needs_clarification_when_target_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = self.clarifier.clarify("fix it", Path(tmp_dir))
        self.assertEqual(result.status, "needs_clarification")
        self.assertIn("target", result.missing_constraints)

    def test_needs_clarification_for_short_continuation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = self.clarifier.clarify("好", Path(tmp_dir))
        self.assertEqual(result.status, "needs_clarification")
        self.assertIn("continuation_context", result.missing_constraints)

    def test_needs_clarification_when_repo_target_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = self.clarifier.clarify("write tests for missing_module.py", Path(tmp_dir))
        self.assertEqual(result.status, "needs_clarification")
        self.assertIn("repo_target", result.missing_constraints)

    def test_normalized_when_whitespace_is_trimmed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            target = repo_path / "planner.py"
            target.write_text("print('ok')\n", encoding="utf-8")
            result = self.clarifier.clarify("  write tests for planner.py  ", repo_path)
        self.assertEqual(result.status, "normalized")
        self.assertEqual(result.normalized_prompt, "write tests for planner.py")

    def test_uses_workflow_clarification_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            target = repo_path / "planner.py"
            target.write_text("print('ok')\n", encoding="utf-8")
            result = self.clarifier.clarify("planner.py", repo_path, explicit_task_type="write_tests")
        self.assertEqual(result.status, "needs_clarification")
        self.assertIn("success_criteria", result.missing_constraints)


if __name__ == "__main__":
    unittest.main()
