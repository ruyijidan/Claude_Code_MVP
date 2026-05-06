from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.daemon.service import DaemonService


class DaemonServiceTests(unittest.TestCase):
    def test_run_task_and_status_roundtrip(self) -> None:
        root = Path(__file__).resolve().parents[1]
        service = DaemonService(root / "specs")
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            result = service.run_task(
                repo_path=str(repo_path),
                request_prompt="Add a tool router and tests",
                task_name="implement_feature",
            )

            self.assertEqual(result["status"], "passed")
            self.assertEqual(result["workflow_status"], "completed")
            self.assertGreaterEqual(result["agent_transition_count"], 5)

            status = service.run_status(repo_path=str(repo_path))
            self.assertTrue(status["available"])
            self.assertEqual(status["status"], "passed")
            self.assertGreaterEqual(status["agent_transition_count"], 5)

            latest = service.latest_run(repo_path=str(repo_path))
            self.assertIsNotNone(latest)
            self.assertIn("agent_transitions", latest)


if __name__ == "__main__":
    unittest.main()
