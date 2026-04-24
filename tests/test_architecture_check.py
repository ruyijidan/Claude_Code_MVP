from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.check_architecture as architecture_check


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

    def test_size_guard_detects_oversized_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            target = root / "app" / "cli" / "main.py"
            target.parent.mkdir(parents=True)
            target.write_text("\n".join("print('x')" for _ in range(5)) + "\n", encoding="utf-8")
            with patch.object(
                architecture_check,
                "SIZE_RULES",
                [{"path": target, "max_lines": 3, "message": "too large"}],
            ):
                violations = architecture_check.find_size_violations(root)

        self.assertEqual(len(violations), 1)
        self.assertIn("too large", violations[0])


if __name__ == "__main__":
    unittest.main()
