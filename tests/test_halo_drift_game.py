import unittest
from pathlib import Path


class HaloDriftGameTests(unittest.TestCase):
    def test_game_script_mentions_long_task_mode(self) -> None:
        game_script = Path("examples/halo-drift/game.js")
        self.assertTrue(game_script.exists())
        text = game_script.read_text(encoding="utf-8")
        self.assertIn("长任务", text)


if __name__ == "__main__":
    unittest.main()
