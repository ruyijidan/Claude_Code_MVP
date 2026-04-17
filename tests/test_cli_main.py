from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.cli.main import main


class CliMainTests(unittest.TestCase):
    def test_cli_runs_prompt_and_prints_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            stream = io.StringIO()
            with redirect_stdout(stream):
                exit_code = main(["fix failing tests", "--repo", str(repo_path)])
            output = stream.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("provider: local", output)
            self.assertIn("task: fix_bug", output)
            self.assertIn("mode: local_loop", output)

    def test_cli_can_show_git_status_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            stream = io.StringIO()
            with redirect_stdout(stream):
                exit_code = main(["--repo", str(repo_path), "--show-status", "--json"])
            output = stream.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("git_status", output)

    def test_cli_can_show_review_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            stream = io.StringIO()
            with redirect_stdout(stream):
                exit_code = main(["--repo", str(repo_path), "--show-review", "--json"])
            output = stream.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("git_review", output)

    def test_cli_can_show_commit_summary_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            stream = io.StringIO()
            with redirect_stdout(stream):
                exit_code = main(["--repo", str(repo_path), "--show-commit-summary", "--json"])
            output = stream.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("git_commit_summary", output)

    def test_cli_can_show_permissions_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            stream = io.StringIO()
            with redirect_stdout(stream):
                exit_code = main(["--repo", str(repo_path), "--show-permissions", "--json"])
            output = stream.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("permissions", output)
            self.assertIn("operations", output)
            self.assertIn("command_profiles", output)
            self.assertIn("write_profiles", output)
            self.assertIn("local_loop", output)
            self.assertIn("delegated_provider", output)
            self.assertIn("dangerous_remove", output)
            self.assertIn("git_metadata", output)

    def test_cli_blocks_delegated_provider_without_explicit_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            stream = io.StringIO()
            with redirect_stdout(stream):
                exit_code = main(
                    [
                        "fix failing tests",
                        "--repo",
                        str(repo_path),
                        "--provider",
                        "codex_cli",
                        "--delegate-to-provider",
                        "--json",
                    ]
                )
            output = stream.getvalue()
            self.assertEqual(exit_code, 1)
            self.assertIn("permission_denied", output)

    def test_cli_blocks_delegated_provider_when_provider_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            stream = io.StringIO()
            fake_adapter = MagicMock()
            fake_adapter.provider_name = "codex_cli"
            fake_adapter.provider_info.return_value = {"provider": "codex_cli", "available": False, "delegates_prompt": False}
            with patch("app.cli.main.build_runtime_adapter", return_value=fake_adapter):
                with redirect_stdout(stream):
                    exit_code = main(
                        [
                            "fix failing tests",
                            "--repo",
                            str(repo_path),
                            "--provider",
                            "codex_cli",
                            "--delegate-to-provider",
                            "--auto-approve",
                            "--json",
                        ]
                    )
            output = stream.getvalue()
            self.assertEqual(exit_code, 1)
            self.assertIn("provider_unavailable", output)

    def test_cli_defaults_claude_code_to_cli_auth_loading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            stream = io.StringIO()
            fake_adapter = MagicMock()
            fake_adapter.provider_name = "claude_code"
            fake_adapter.provider_info.return_value = {"provider": "claude_code", "available": True, "delegates_prompt": True}
            fake_adapter.can_delegate_prompt.return_value = True
            fake_adapter.execute_prompt.return_value = (0, '{"type":"result","result":"MODEL_OK"}', ["claude"])
            with patch("app.cli.main.load_project_env", return_value=(None, {})) as load_env:
                with patch("app.cli.main.build_runtime_adapter", return_value=fake_adapter):
                    with redirect_stdout(stream):
                        exit_code = main(
                            [
                                "Reply with exactly MODEL_OK",
                                "--repo",
                                str(repo_path),
                                "--provider",
                                "claude_code",
                                "--delegate-to-provider",
                                "--auto-approve",
                                "--json",
                            ]
                        )
            self.assertEqual(exit_code, 0)
            load_env.assert_called_once_with(repo_path.resolve(), exclude_prefixes=("ANTHROPIC_",))

    def test_cli_can_force_env_auth_loading_for_claude_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            stream = io.StringIO()
            fake_adapter = MagicMock()
            fake_adapter.provider_name = "claude_code"
            fake_adapter.provider_info.return_value = {"provider": "claude_code", "available": True, "delegates_prompt": True}
            fake_adapter.can_delegate_prompt.return_value = True
            fake_adapter.execute_prompt.return_value = (0, '{"type":"result","result":"MODEL_OK"}', ["claude"])
            with patch("app.cli.main.load_project_env", return_value=(None, {})) as load_env:
                with patch("app.cli.main.build_runtime_adapter", return_value=fake_adapter):
                    with redirect_stdout(stream):
                        exit_code = main(
                            [
                                "Reply with exactly MODEL_OK",
                                "--repo",
                                str(repo_path),
                                "--provider",
                                "claude_code",
                                "--auth-source",
                                "env",
                                "--delegate-to-provider",
                                "--auto-approve",
                                "--json",
                            ]
                        )
            self.assertEqual(exit_code, 0)
            load_env.assert_called_once_with(repo_path.resolve(), exclude_prefixes=())

    def test_cli_can_delegate_to_glm5_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            stream = io.StringIO()
            fake_adapter = MagicMock()
            fake_adapter.provider_name = "glm5"
            fake_adapter.provider_info.return_value = {"provider": "glm5", "available": True, "delegates_prompt": True}
            fake_adapter.can_delegate_prompt.return_value = True
            fake_adapter.execute_prompt.return_value = (0, '{"result":"MODEL_OK"}', ["POST", "https://example.test/v1/messages"])
            with patch("app.cli.main.load_project_env", return_value=(None, {})) as load_env:
                with patch("app.cli.main.build_runtime_adapter", return_value=fake_adapter):
                    with redirect_stdout(stream):
                        exit_code = main(
                            [
                                "Reply with exactly MODEL_OK",
                                "--repo",
                                str(repo_path),
                                "--provider",
                                "glm5",
                                "--delegate-to-provider",
                                "--auto-approve",
                                "--json",
                            ]
                        )
            self.assertEqual(exit_code, 0)
            load_env.assert_called_once_with(repo_path.resolve(), exclude_prefixes=())
            self.assertIn('"provider": "glm5"', stream.getvalue())

    def test_cli_can_show_post_review_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            stream = io.StringIO()
            fake_result = {
                "runtime_provider": "local",
                "task_spec": type("TaskSpecStub", (), {"name": "fix_bug"})(),
                "test_result": "passed",
                "changed_files": ["a.py"],
                "repo_context": {"git": {"branch": {"name": "main"}}},
                "trajectory_path": str(repo_path / "traj.json"),
            }
            fake_changed_files = {"available": True, "files": ["a.py", "b.py"]}
            fake_review = {
                "available": True,
                "summary": "2 file(s) changed, +5/-1 lines. Top files: a.py, b.py",
                "stats": {
                    "files": [
                        {"path": "a.py", "added": 4, "deleted": 1},
                        {"path": "b.py", "added": 1, "deleted": 0},
                    ]
                },
            }
            with patch("app.cli.main.CodingAgentLoop.run", return_value=fake_result):
                with patch("app.cli.main.GitTool.changed_files", return_value=fake_changed_files):
                    with patch("app.cli.main.GitTool.review_summary", return_value=fake_review):
                        with redirect_stdout(stream):
                            exit_code = main(["fix bug", "--repo", str(repo_path), "--show-post-review"])
            output = stream.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("post changed files:", output)
            self.assertIn("a.py", output)
            self.assertIn("post review:", output)
            self.assertIn("+5/-1", output)

    def test_cli_can_show_post_commit_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            stream = io.StringIO()
            fake_result = {
                "runtime_provider": "local",
                "task_spec": type("TaskSpecStub", (), {"name": "fix_bug"})(),
                "test_result": "passed",
                "changed_files": ["a.py"],
                "repo_context": {"git": {"branch": {"name": "main"}}},
                "trajectory_path": str(repo_path / "traj.json"),
            }
            fake_commit_summary = {
                "available": True,
                "title": "feat: update app",
                "summary": "2 file(s) changed, +5/-1 lines. Top files: a.py, b.py",
            }
            with patch("app.cli.main.CodingAgentLoop.run", return_value=fake_result):
                with patch("app.cli.main.GitTool.suggested_commit_message", return_value=fake_commit_summary):
                    with redirect_stdout(stream):
                        exit_code = main(["fix bug", "--repo", str(repo_path), "--show-post-commit-summary"])
            output = stream.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("post commit summary:", output)
            self.assertIn("feat: update app", output)


if __name__ == "__main__":
    unittest.main()
