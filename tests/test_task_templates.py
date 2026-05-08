from __future__ import annotations

import unittest

from app.core.task_templates import build_task_artifacts


class TaskTemplateTests(unittest.TestCase):
    def test_long_task_game_targets_halo_drift(self) -> None:
        artifacts = build_task_artifacts("long_task_game")

        self.assertEqual(artifacts["module_path"], "examples/halo-drift/game.js")
        self.assertEqual(artifacts["test_path"], "tests/test_halo_drift_game.py")
        self.assertIn("长任务", artifacts["module_content"])


if __name__ == "__main__":
    unittest.main()
