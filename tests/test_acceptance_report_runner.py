from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.acceptance.report_runner import build_acceptance_prompt, run_acceptance_report


class AcceptanceReportRunnerTests(unittest.TestCase):
    def test_build_acceptance_prompt_uses_summaries(self) -> None:
        prompt = build_acceptance_prompt(
            {
                "readme": "readme summary",
                "architecture": "architecture summary",
                "testing_conventions": "testing summary",
                "current_sprint": "sprint summary",
                "release_notes": "release notes summary",
                "git_status": "git status summary",
                "git_diff_stat": "git diff summary",
            }
        )
        self.assertIn("README_SUMMARY", prompt)
        self.assertIn("ARCHITECTURE_SUMMARY", prompt)
        self.assertIn("GIT_DIFF_STAT_SUMMARY", prompt)
        self.assertIn("keep system_summary concise", prompt)

    def test_writes_markdown_and_json_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            (repo_path / "docs" / "conventions").mkdir(parents=True)
            (repo_path / "docs" / "plans").mkdir(parents=True)
            (repo_path / "README.md").write_text("readme\n", encoding="utf-8")
            (repo_path / "ARCHITECTURE.md").write_text("architecture\n", encoding="utf-8")
            (repo_path / "docs" / "conventions" / "testing.md").write_text("testing\n", encoding="utf-8")
            (repo_path / "docs" / "plans" / "current-sprint.md").write_text("sprint\n", encoding="utf-8")
            (repo_path / "docs" / "plans" / "release-notes.md").write_text("notes\n", encoding="utf-8")
            output_dir = repo_path / ".claude-code" / "acceptance"
            model_response = json.dumps(
                {
                    "system_summary": "Summary",
                    "provider_risks": ["Risk one"],
                    "live_acceptance_configured": True,
                    "acceptance_status": "READY",
                    "evidence": ["Evidence one"],
                }
            )

            with patch("app.acceptance.report_runner.load_project_env", return_value=(None, {})):
                with patch("app.acceptance.report_runner.resolve_auth_loading_policy", return_value=("glm5", ())):
                    with patch("app.acceptance.report_runner.build_model_client") as build_client:
                        build_client.return_value.generate.return_value = model_response
                        result = run_acceptance_report(repo_path, "glm5", output_dir)

            self.assertEqual(result["acceptance_status"], "READY")
            self.assertTrue((output_dir / "final_acceptance_report.json").exists())
            self.assertTrue((output_dir / "final_acceptance_report.md").exists())

    def test_rejects_invalid_acceptance_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            (repo_path / "docs" / "conventions").mkdir(parents=True)
            (repo_path / "docs" / "plans").mkdir(parents=True)
            (repo_path / "README.md").write_text("readme\n", encoding="utf-8")
            (repo_path / "ARCHITECTURE.md").write_text("architecture\n", encoding="utf-8")
            (repo_path / "docs" / "conventions" / "testing.md").write_text("testing\n", encoding="utf-8")
            (repo_path / "docs" / "plans" / "current-sprint.md").write_text("sprint\n", encoding="utf-8")
            (repo_path / "docs" / "plans" / "release-notes.md").write_text("notes\n", encoding="utf-8")
            output_dir = repo_path / ".claude-code" / "acceptance"
            model_response = json.dumps(
                {
                    "system_summary": "Summary",
                    "provider_risks": ["Risk one"],
                    "live_acceptance_configured": True,
                    "acceptance_status": "INVALID",
                    "evidence": ["Evidence one"],
                }
            )

            with patch("app.acceptance.report_runner.load_project_env", return_value=(None, {})):
                with patch("app.acceptance.report_runner.resolve_auth_loading_policy", return_value=("glm5", ())):
                    with patch("app.acceptance.report_runner.build_model_client") as build_client:
                        build_client.return_value.generate.return_value = model_response
                        with self.assertRaises(ValueError):
                            run_acceptance_report(repo_path, "glm5", output_dir)
