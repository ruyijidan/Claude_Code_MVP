from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


class AgentVerifyScriptTests(unittest.TestCase):
    def test_verify_script_has_expected_steps(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "agent_verify.sh"
        content = script.read_text(encoding="utf-8")
        self.assertIn("worktree add", content)
        self.assertIn("python3 scripts/check_architecture.py", content)
        self.assertIn("python3 -m unittest discover -s tests", content)

    def test_architecture_check_script_runs(self) -> None:
        root = Path(__file__).resolve().parents[1]
        completed = subprocess.run(
            ["python3", "scripts/check_architecture.py"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
