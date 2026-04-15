from __future__ import annotations

import unittest
from pathlib import Path

from app.core.spec_loader import SpecLoader


class SpecLoaderTests(unittest.TestCase):
    def test_load_task(self) -> None:
        root = Path(__file__).resolve().parents[1] / "specs"
        loader = SpecLoader(root)
        task = loader.load_task("implement_feature")
        self.assertEqual(task.name, "implement_feature")
        self.assertIn("feature_request", task.inputs)


if __name__ == "__main__":
    unittest.main()
