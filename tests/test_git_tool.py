from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from app.runtime.git_tool import GitTool
from app.runtime.local_runtime import LocalRuntimeAdapter


class GitToolTests(unittest.TestCase):
    def test_snapshot_for_non_git_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            tool = GitTool(LocalRuntimeAdapter())
            snapshot = tool.snapshot(repo_path)
            self.assertFalse(snapshot["available"])

    def test_snapshot_for_git_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True, text=True)
            (repo_path / "hello.txt").write_text("hello\n", encoding="utf-8")
            tool = GitTool(LocalRuntimeAdapter())
            snapshot = tool.snapshot(repo_path)
            self.assertTrue(snapshot["available"])
            self.assertIn("hello.txt", snapshot["status"]["summary"])
            self.assertIsNotNone(snapshot["branch"]["name"])
            self.assertIn("hello.txt", snapshot["review"]["summary"])

    def test_review_summary_reports_numstat(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True, text=True)
            file_path = repo_path / "hello.txt"
            file_path.write_text("hello\nworld\n", encoding="utf-8")
            tool = GitTool(LocalRuntimeAdapter())
            review = tool.review_summary(repo_path)
            self.assertTrue(review["available"])
            self.assertIn("hello.txt", review["files"])
            self.assertGreaterEqual(review["stats"]["total_added"], 0)

    def test_suggested_commit_message_uses_changed_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True, text=True)
            file_path = repo_path / "README.md"
            file_path.write_text("docs\n", encoding="utf-8")
            tool = GitTool(LocalRuntimeAdapter())
            commit_summary = tool.suggested_commit_message(repo_path)
            self.assertTrue(commit_summary["available"])
            self.assertIn("docs:", commit_summary["title"])


if __name__ == "__main__":
    unittest.main()
