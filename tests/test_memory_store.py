from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.core.memory_store import MemoryStore


class MemoryStoreTests(unittest.TestCase):
    def test_search_related_returns_repo_scoped_hits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            repo_path = root / "repo"
            repo_path.mkdir()
            other_repo_path = root / "other"
            other_repo_path.mkdir()
            store = MemoryStore(root / "memories")
            store.write(
                "20260430T080000Z",
                {
                    "task": "write_tests",
                    "request_prompt": "write tests for planner.py",
                    "request_repo_path": str(repo_path),
                    "changed_files": ["planner.py", "tests/test_planner.py"],
                    "test_result": "passed",
                },
            )
            store.write(
                "20260430T090000Z",
                {
                    "task": "implement_feature",
                    "request_prompt": "add metrics dashboard",
                    "request_repo_path": str(other_repo_path),
                    "changed_files": ["dashboard.py"],
                    "test_result": "passed",
                },
            )

            hits = store.search_related("planner.py tests", repo_path, task_name="write_tests")

        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["task"], "write_tests")
        self.assertIn("planner.py", hits[0]["request_prompt"])
        self.assertGreater(hits[0]["score"], 0)


if __name__ == "__main__":
    unittest.main()
