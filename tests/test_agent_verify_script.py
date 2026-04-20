from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


class AgentVerifyScriptTests(unittest.TestCase):
    def test_verify_script_has_expected_steps(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "agent_verify.sh"
        content = script.read_text(encoding="utf-8")
        self.assertIn("worktree add", content)
        self.assertIn("python3 scripts/check_architecture.py", content)
        self.assertIn("python3 -m unittest discover -s tests", content)

    def test_architecture_check_script_runs(self) -> None:
        root = Path(__file__).resolve().parents[1]
        completed = subprocess.run(
            ["python3", "scripts/check_architecture.py"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_release_acceptance_script_has_expected_steps(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "release_acceptance.sh"
        content = script.read_text(encoding="utf-8")
        self.assertIn("python3 -m unittest discover -s", content)
        self.assertIn("tests.test_live_provider_integration", content)
        self.assertIn("CC_RUN_LIVE_ACCEPTANCE_TASK", content)
        self.assertIn("run_with_optional_timeout", content)
        self.assertIn("final_acceptance_report.md", content)
        self.assertIn("final_acceptance_report.json", content)
        self.assertIn("acceptance-task-template.md", content)
        self.assertIn("validate_acceptance_report_json", content)
        self.assertIn("invalid acceptance_status", content)

    def test_acceptance_task_template_has_expected_placeholders(self) -> None:
        root = Path(__file__).resolve().parents[1]
        template = root / "specs" / "templates" / "acceptance-task-template.md"
        content = template.read_text(encoding="utf-8")
        self.assertIn("{timeout_minutes}", content)
        self.assertIn("{report_markdown_path}", content)
        self.assertIn("{report_json_path}", content)

    def test_acceptance_report_design_doc_describes_contract(self) -> None:
        root = Path(__file__).resolve().parents[1]
        doc = root / "docs" / "design" / "acceptance-report.md"
        content = doc.read_text(encoding="utf-8")
        self.assertIn("acceptance_status", content)
        self.assertIn("READY", content)
        self.assertIn("NEEDS_REVIEW", content)
        self.assertIn("BLOCKED", content)

    def test_acceptance_report_examples_match_contract(self) -> None:
        root = Path(__file__).resolve().parents[1]
        markdown_example = root / "docs" / "design" / "acceptance-report-example.md"
        json_example = root / "docs" / "design" / "acceptance-report-example.json"
        markdown_content = markdown_example.read_text(encoding="utf-8")
        json_content = json_example.read_text(encoding="utf-8")
        self.assertIn("ACCEPTANCE_STATUS: NEEDS_REVIEW", markdown_content)
        self.assertIn('"acceptance_status": "NEEDS_REVIEW"', json_content)
        self.assertIn('"system_summary"', json_content)
        self.assertIn('"provider_risks"', json_content)
        self.assertIn('"live_acceptance_configured"', json_content)
        self.assertIn('"evidence"', json_content)


if __name__ == "__main__":
    unittest.main()
