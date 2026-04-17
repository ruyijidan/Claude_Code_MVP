from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.agent.policies import ExecutionPolicy, PermissionPipeline, make_command_guard
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


if __name__ == "__main__":
    unittest.main()
