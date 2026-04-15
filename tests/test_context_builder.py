from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import subprocess

from app.agent.context_builder import RepoContextBuilder
from app.runtime.local_runtime import LocalRuntimeAdapter


class ContextBuilderTests(unittest.TestCase):
    def test_collects_candidate_files_without_git(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            (repo_path / "src").mkdir()
            (repo_path / "docs" / "architecture").mkdir(parents=True)
            (repo_path / "AGENTS.md").write_text("# agents\n", encoding="utf-8")
            (repo_path / "ARCHITECTURE.md").write_text("# architecture\n", encoding="utf-8")
            (repo_path / "docs" / "architecture" / "boundaries.md").write_text("# boundaries\n", encoding="utf-8")
            (repo_path / "src" / "main.py").write_text("print('hi')\n", encoding="utf-8")

            builder = RepoContextBuilder(LocalRuntimeAdapter())
            result = builder.build(repo_path, "inspect repo")

            self.assertEqual(result["git"]["available"], False)
            self.assertIn("src/main.py", result["candidate_files"])
            self.assertIn("AGENTS.md", result["always_include_docs"])
            self.assertIn("src/main.py", result["likely_relevant_files"])
            self.assertEqual(result["scoped_context"]["repo_path"], str(repo_path))

    def test_collects_git_snapshot_for_git_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True, text=True)
            (repo_path / "src").mkdir()
            (repo_path / "tests").mkdir()
            (repo_path / "docs" / "architecture").mkdir(parents=True)
            (repo_path / "AGENTS.md").write_text("# agents\n", encoding="utf-8")
            (repo_path / "ARCHITECTURE.md").write_text("# architecture\n", encoding="utf-8")
            (repo_path / "docs" / "architecture" / "boundaries.md").write_text("# boundaries\n", encoding="utf-8")
            (repo_path / "src" / "main.py").write_text("print('hi')\n", encoding="utf-8")
            (repo_path / "tests" / "test_main.py").write_text("print('test')\n", encoding="utf-8")

            builder = RepoContextBuilder(LocalRuntimeAdapter())
            result = builder.build(repo_path, "write tests for main")

            self.assertTrue(result["git"]["available"])
            self.assertIn("src/main.py", result["candidate_files"])
            self.assertIn("src", result["git"]["status"]["summary"])
            self.assertIn("tests/test_main.py", result["test_targets"])
            self.assertIn("docs/architecture/boundaries.md", result["architecture_constraints"])


if __name__ == "__main__":
    unittest.main()
