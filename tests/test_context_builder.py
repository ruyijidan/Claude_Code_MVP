from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import subprocess

from app.agent.context_builder import RepoContextBuilder
from app.core.memory_store import MemoryStore
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
            self.assertIn("inspect repo", result["prompt_summary"])
            self.assertIn("AGENTS.md", result["always_include_docs"])
            self.assertIn("src/main.py", result["likely_relevant_files"])
            self.assertIn("src/main.py", result["candidate_files_summary"])
            self.assertEqual(result["context_budget"]["max_candidate_files"], 12)
            self.assertTrue(any(item["path"] == "src/main.py" for item in result["candidate_file_summaries"]))
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
            self.assertIn("src/", result["git_summary_compact"]["status_summary"])
            self.assertIn("tests/test_main.py", result["test_targets"])
            self.assertIn("tests/test_main.py", result["test_targets_summary"])
            self.assertIn("docs/architecture/boundaries.md", result["architecture_constraints"])

    def test_budgeted_file_summary_truncates_large_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            (repo_path / "src").mkdir()
            (repo_path / "docs" / "architecture").mkdir(parents=True)
            (repo_path / "AGENTS.md").write_text("# agents\n", encoding="utf-8")
            (repo_path / "ARCHITECTURE.md").write_text("# architecture\n", encoding="utf-8")
            (repo_path / "docs" / "architecture" / "boundaries.md").write_text("# boundaries\n", encoding="utf-8")
            large_text = ("hello world\n" * 100) + "tail marker\n"
            (repo_path / "src" / "main.py").write_text(large_text, encoding="utf-8")

            builder = RepoContextBuilder(LocalRuntimeAdapter())
            result = builder.build(repo_path, "inspect main")

        main_summary = next(item["summary"] for item in result["candidate_file_summaries"] if item["path"] == "src/main.py")
        self.assertIn("...\n", main_summary)
        self.assertIn("tail marker", main_summary)

    def test_includes_application_legibility_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            (repo_path / "src").mkdir()
            (repo_path / "logs").mkdir()
            (repo_path / "examples" / "preview").mkdir(parents=True)
            (repo_path / "reports").mkdir()
            (repo_path / "docs" / "architecture").mkdir(parents=True)
            (repo_path / "AGENTS.md").write_text("# agents\n", encoding="utf-8")
            (repo_path / "ARCHITECTURE.md").write_text("# architecture\n", encoding="utf-8")
            (repo_path / "docs" / "architecture" / "boundaries.md").write_text("# boundaries\n", encoding="utf-8")
            (repo_path / "src" / "main.py").write_text("print('hi')\n", encoding="utf-8")
            (repo_path / "logs" / "agent.log").write_text("run ok\n", encoding="utf-8")
            (repo_path / "examples" / "preview" / "index.html").write_text("<html>preview</html>\n", encoding="utf-8")
            (repo_path / "reports" / "coverage.json").write_text('{"line_rate": 1.0}\n', encoding="utf-8")

            builder = RepoContextBuilder(LocalRuntimeAdapter())
            result = builder.build(repo_path, "inspect runtime artifacts")

        legibility = result["application_legibility"]
        self.assertTrue(legibility["available"])
        self.assertIn("logs/agent.log", legibility["log_files"])
        self.assertIn("examples/preview/index.html", legibility["preview_targets"])
        self.assertIn("reports/coverage.json", legibility["metric_files"])

    def test_includes_related_memory_hits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            (repo_path / "src").mkdir()
            (repo_path / "docs" / "architecture").mkdir(parents=True)
            (repo_path / "AGENTS.md").write_text("# agents\n", encoding="utf-8")
            (repo_path / "ARCHITECTURE.md").write_text("# architecture\n", encoding="utf-8")
            (repo_path / "docs" / "architecture" / "boundaries.md").write_text("# boundaries\n", encoding="utf-8")
            (repo_path / "src" / "planner.py").write_text("print('hi')\n", encoding="utf-8")
            memory_store = MemoryStore(repo_path / ".claude-code" / "trajectories")
            memory_store.write(
                "20260430T080000Z",
                {
                    "task": "write_tests",
                    "request_prompt": "write tests for planner.py",
                    "request_repo_path": str(repo_path),
                    "changed_files": ["planner.py", "tests/test_planner.py"],
                },
            )

            builder = RepoContextBuilder(LocalRuntimeAdapter(), memory_store=memory_store)
            result = builder.build(repo_path, "write tests for planner.py", task_name="write_tests")

        self.assertEqual(len(result["memory_hits"]), 1)
        self.assertIn("write_tests", result["memory_hits_summary"])
        self.assertEqual(result["memory_context_paths"][0], "planner.py")
        self.assertIn("planner.py", result["memory_context_paths_summary"])


if __name__ == "__main__":
    unittest.main()
