from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.runtime.cli_adapter import ClaudeCodeAdapter, CodexCLIAdapter


class ProviderDelegationTests(unittest.TestCase):
    def test_claude_adapter_builds_noninteractive_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            adapter = ClaudeCodeAdapter()
            adapter.run_command = lambda cmd, cwd: (0, "ok")  # type: ignore[method-assign]
            code, output, command = adapter.execute_prompt("fix failing tests", Path(tmp_dir), auto_approve=False)
            self.assertIsInstance(code, int)
            self.assertIsInstance(output, str)
            self.assertEqual(command[:4], ["claude", "-p", "--output-format", "json"])

    def test_codex_adapter_builds_exec_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            adapter = CodexCLIAdapter()
            adapter.run_command = lambda cmd, cwd: (0, "ok")  # type: ignore[method-assign]
            code, output, command = adapter.execute_prompt("fix failing tests", Path(tmp_dir), auto_approve=False)
            self.assertIsInstance(code, int)
            self.assertIsInstance(output, str)
            self.assertEqual(command[:2], ["codex", "--cd"])
            self.assertIn("--skip-git-repo-check", command)
            self.assertIn("--full-auto", command)


if __name__ == "__main__":
    unittest.main()
