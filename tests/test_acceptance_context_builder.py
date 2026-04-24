from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from app.acceptance.context_builder import (
    GIT_DIFF_STAT_SNAPSHOT_PATH,
    GIT_STATUS_SNAPSHOT_PATH,
    build_acceptance_context,
)


class AcceptanceContextBuilderTests(unittest.TestCase):
    def test_builds_acceptance_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            (repo_path / "docs" / "conventions").mkdir(parents=True)
            (repo_path / "docs" / "plans").mkdir(parents=True)
            (repo_path / "README.md").write_text("readme text\n", encoding="utf-8")
            (repo_path / "ARCHITECTURE.md").write_text("architecture text\n", encoding="utf-8")
            (repo_path / "docs" / "conventions" / "testing.md").write_text("testing text\n", encoding="utf-8")
            (repo_path / "docs" / "plans" / "current-sprint.md").write_text("sprint text\n", encoding="utf-8")
            (repo_path / "docs" / "plans" / "release-notes.md").write_text("notes text\n", encoding="utf-8")
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)

            context = build_acceptance_context(repo_path)

        self.assertIn("readme text", context["readme"])
        self.assertIn("architecture text", context["architecture"])
        self.assertIn("testing text", context["testing_conventions"])
        self.assertIn("sprint text", context["current_sprint"])
        self.assertIn("notes text", context["release_notes"])
        self.assertIn("??", context["git_status"])
        self.assertIn("README.md", context["git_status_paths"])

    def test_truncates_large_documents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            (repo_path / "docs" / "conventions").mkdir(parents=True)
            (repo_path / "docs" / "plans").mkdir(parents=True)
            large_text = ("abcde" * 2000) + "\nTAIL\n"
            (repo_path / "README.md").write_text(large_text, encoding="utf-8")
            (repo_path / "ARCHITECTURE.md").write_text(large_text, encoding="utf-8")
            (repo_path / "docs" / "conventions" / "testing.md").write_text(large_text, encoding="utf-8")
            (repo_path / "docs" / "plans" / "current-sprint.md").write_text(large_text, encoding="utf-8")
            (repo_path / "docs" / "plans" / "release-notes.md").write_text(large_text, encoding="utf-8")
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)

            context = build_acceptance_context(repo_path)

        self.assertIn("...\n", context["readme"])
        self.assertLess(len(context["readme"]), len(large_text))
        self.assertIn("TAIL", context["readme"])

    def test_uses_git_snapshot_fallback_when_repo_metadata_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            (repo_path / "docs" / "conventions").mkdir(parents=True)
            (repo_path / "docs" / "plans").mkdir(parents=True)
            (repo_path / ".claude-code" / "acceptance" / "context").mkdir(parents=True)
            (repo_path / "README.md").write_text("readme text\n", encoding="utf-8")
            (repo_path / "ARCHITECTURE.md").write_text("architecture text\n", encoding="utf-8")
            (repo_path / "docs" / "conventions" / "testing.md").write_text("testing text\n", encoding="utf-8")
            (repo_path / "docs" / "plans" / "current-sprint.md").write_text("sprint text\n", encoding="utf-8")
            (repo_path / "docs" / "plans" / "release-notes.md").write_text("notes text\n", encoding="utf-8")
            (repo_path / GIT_STATUS_SNAPSHOT_PATH).write_text("M README.md\n", encoding="utf-8")
            (repo_path / GIT_DIFF_STAT_SNAPSHOT_PATH).write_text("README.md | 10 +++++-----\n", encoding="utf-8")

            context = build_acceptance_context(repo_path)

        self.assertIn("M README.md", context["git_status"])
        self.assertIn("README.md | 10", context["git_diff_stat"])
        self.assertIn("README.md", context["git_status_paths"])
        self.assertIn("README.md", context["git_diff_paths"])
