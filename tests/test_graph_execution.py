from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.core.memory_store import MemoryStore
from app.core.spec_loader import SpecLoader
from app.graph.executor import GraphExecutor


class GraphExecutionTests(unittest.TestCase):
    def test_execute_full_loop(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir) / "workspace"
            repo_path.mkdir()
            loader = SpecLoader(root / "specs")
            executor = GraphExecutor(loader, MemoryStore(Path(tmp_dir) / "logs"))
            result = executor.execute(
                {
                    "repo_path": repo_path,
                    "task_spec": loader.load_task("implement_feature"),
                    "request": {
                        "repo_path": str(repo_path),
                        "feature_request": "Add a tool router and tests",
                    },
                }
            )
            self.assertEqual(result["test_result"], "passed")
            self.assertEqual(result["selected_path"], "complete")
            self.assertEqual(result["workflow_spec"].name, "implement_feature")
            self.assertEqual(result["plan"][0]["id"], "workflow_context")
            self.assertIn("AGENTS.md", result["plan"][0]["description"])
            self.assertEqual(result["plan"][2]["description"], "inspect context and identify the smallest feature surface")
            self.assertTrue(result["completion_check"]["passed"])
            self.assertTrue(all(item["passed"] for item in result["gate_results"]))
            self.assertTrue(Path(result["trajectory_path"]).exists())
            payload = json.loads(Path(result["trajectory_path"]).read_text(encoding="utf-8"))
            self.assertEqual(payload["task"], "implement_feature")
            self.assertEqual(payload["workflow"], "implement_feature")
            self.assertEqual(payload["runtime_provider"], "local")
            self.assertTrue(payload["completion_check"]["passed"])
            self.assertTrue(all(item["passed"] for item in payload["gate_results"]))

    def test_execute_fix_bug_task(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir) / "workspace"
            repo_path.mkdir()
            loader = SpecLoader(root / "specs")
            executor = GraphExecutor(loader, MemoryStore(Path(tmp_dir) / "logs"))
            result = executor.execute(
                {
                    "repo_path": repo_path,
                    "task_spec": loader.load_task("fix_bug"),
                    "request": {
                        "repo_path": str(repo_path),
                        "feature_request": "Fix divide by zero",
                    },
                }
            )
            self.assertEqual(result["test_result"], "passed")
            self.assertIn("calculator.py", "".join(result["changed_files"]))
            self.assertEqual(result["repair_action"], "added_missing_tests")
            self.assertTrue(result["repair_attempts"])
            self.assertEqual(result["repair_attempts"][0]["repair_decision"]["action"], "add_missing_tests")
            self.assertIn("missing_tests", {item["kind"] for item in result["repair_attempts"][0]["failure_signals"]})

    def test_execute_investigate_issue_task(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir) / "workspace"
            repo_path.mkdir()
            loader = SpecLoader(root / "specs")
            executor = GraphExecutor(loader, MemoryStore(Path(tmp_dir) / "logs"), runtime_provider="codex_cli")
            result = executor.execute(
                {
                    "repo_path": repo_path,
                    "task_spec": loader.load_task("investigate_issue"),
                    "request": {
                        "repo_path": str(repo_path),
                        "feature_request": "Investigate router failures",
                    },
                }
            )
            self.assertEqual(result["runtime_provider"], "codex_cli")
            self.assertEqual(result["test_result"], "passed")
            self.assertIn("investigation.md", "".join(result["changed_files"]))


if __name__ == "__main__":
    unittest.main()
