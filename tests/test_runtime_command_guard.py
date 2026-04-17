from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.agent.policies import ExecutionPolicy, PermissionPipeline, make_command_guard, make_file_write_guard
from app.runtime.local_runtime import LocalRuntimeAdapter


class RuntimeCommandGuardTests(unittest.TestCase):
    def test_guard_blocks_high_risk_command_before_execution(self) -> None:
        adapter = LocalRuntimeAdapter()
        pipeline = PermissionPipeline()
        adapter.configure_command_guard(make_command_guard(pipeline, ExecutionPolicy(), provider_info=adapter.provider_info()))

        code, output = adapter.run_command(["rm", "-rf", "/tmp/example"], Path("."))

        self.assertEqual(code, 126)
        self.assertIn("permission denied before execution", output)
        self.assertIn("High-risk system mutation commands", output)

    def test_guard_allows_repository_test_command(self) -> None:
        adapter = LocalRuntimeAdapter()
        pipeline = PermissionPipeline()
        adapter.configure_command_guard(make_command_guard(pipeline, ExecutionPolicy(), provider_info=adapter.provider_info()))

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            tests_dir = repo_path / "tests"
            tests_dir.mkdir()
            (tests_dir / "test_smoke.py").write_text(
                "import unittest\n\n"
                "class SmokeTests(unittest.TestCase):\n"
                "    def test_ok(self):\n"
                "        self.assertTrue(True)\n\n"
                "if __name__ == '__main__':\n"
                "    unittest.main()\n",
                encoding="utf-8",
            )

            code, output = adapter.run_command(["python3", "-m", "unittest", "discover", "-s", "tests"], repo_path)

        self.assertEqual(code, 0)
        self.assertIn("OK", output)

    def test_file_guard_blocks_writes_outside_repo(self) -> None:
        adapter = LocalRuntimeAdapter()
        pipeline = PermissionPipeline()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir) / "repo"
            repo_path.mkdir()
            outside_path = Path(tmp_dir) / "outside.txt"
            adapter.configure_file_guard(make_file_write_guard(pipeline, repo_root=repo_path))

            with self.assertRaises(PermissionError):
                adapter.edit_file(outside_path, "blocked\n")

    def test_file_guard_blocks_writes_to_git_metadata(self) -> None:
        adapter = LocalRuntimeAdapter()
        pipeline = PermissionPipeline()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            (repo_path / ".git").mkdir()
            adapter.configure_file_guard(make_file_write_guard(pipeline, repo_root=repo_path))

            with self.assertRaises(PermissionError):
                adapter.edit_file(repo_path / ".git" / "config", "blocked\n")

    def test_file_guard_allows_repo_local_writes(self) -> None:
        adapter = LocalRuntimeAdapter()
        pipeline = PermissionPipeline()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            target = repo_path / "sample_app" / "tool_router.py"
            adapter.configure_file_guard(make_file_write_guard(pipeline, repo_root=repo_path))

            adapter.edit_file(target, "print('ok')\n")

            self.assertEqual(target.read_text(encoding="utf-8"), "print('ok')\n")

    def test_file_guard_allows_runtime_artifact_writes(self) -> None:
        adapter = LocalRuntimeAdapter()
        pipeline = PermissionPipeline()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            target = repo_path / ".claude-code" / "trajectories" / "run.json"
            adapter.configure_file_guard(make_file_write_guard(pipeline, repo_root=repo_path))

            adapter.edit_file(target, "{\"ok\": true}\n")

            self.assertEqual(target.read_text(encoding="utf-8"), "{\"ok\": true}\n")

    def test_file_guard_blocks_unclassified_directory_writes_by_default(self) -> None:
        adapter = LocalRuntimeAdapter()
        pipeline = PermissionPipeline()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            target = repo_path / "tmp" / "scratch.txt"
            adapter.configure_file_guard(make_file_write_guard(pipeline, repo_root=repo_path))

            with self.assertRaises(PermissionError):
                adapter.edit_file(target, "blocked\n")

    def test_file_guard_allows_unclassified_directory_writes_in_auto_mode(self) -> None:
        adapter = LocalRuntimeAdapter()
        pipeline = PermissionPipeline()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            target = repo_path / "tmp" / "scratch.txt"
            adapter.configure_file_guard(
                make_file_write_guard(
                    pipeline,
                    repo_root=repo_path,
                    policy=ExecutionPolicy(auto_approve=True),
                )
            )

            adapter.edit_file(target, "allowed\n")

            self.assertEqual(target.read_text(encoding="utf-8"), "allowed\n")


if __name__ == "__main__":
    unittest.main()
