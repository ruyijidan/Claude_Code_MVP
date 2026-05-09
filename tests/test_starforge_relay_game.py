from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


class StarforgeRelayGameTests(unittest.TestCase):
    def test_game_assets_exist(self) -> None:
        root = Path("examples/starforge-relay")
        self.assertTrue((root / "index.html").exists())
        self.assertTrue((root / "styles.css").exists())
        self.assertTrue((root / "game.js").exists())
        self.assertTrue((root / "README.md").exists())

    def test_game_script_parses(self) -> None:
        completed = subprocess.run(
            ["node", "--check", "examples/starforge-relay/game.js"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()
