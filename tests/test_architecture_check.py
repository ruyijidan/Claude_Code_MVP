from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


class ArchitectureCheckTests(unittest.TestCase):
    def test_architecture_check_passes_for_current_repo(self) -> None:
        root = Path(__file__).resolve().parents[1]
        completed = subprocess.run(
            ["python3", "scripts/check_architecture.py"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("passed", completed.stdout.lower())


if __name__ == "__main__":
    unittest.main()
