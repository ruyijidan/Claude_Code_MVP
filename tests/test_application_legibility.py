from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.runtime.application_legibility import ApplicationLegibilityCollector


class ApplicationLegibilityCollectorTests(unittest.TestCase):
    def test_collects_preview_log_and_metric_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            (repo_path / "examples" / "web-game").mkdir(parents=True)
            (repo_path / "logs").mkdir()
            (repo_path / "reports").mkdir()
            (repo_path / "examples" / "web-game" / "index.html").write_text(
                "<html><body>preview</body></html>\n",
                encoding="utf-8",
            )
            (repo_path / "logs" / "agent.log").write_text("verification passed\n", encoding="utf-8")
            (repo_path / "reports" / "coverage.json").write_text('{"line_rate": 0.95}\n', encoding="utf-8")

            result = ApplicationLegibilityCollector().collect(repo_path)

        self.assertTrue(result["available"])
        self.assertIn("examples/web-game/index.html", result["preview_targets"])
        self.assertIn("logs/agent.log", result["log_files"])
        self.assertIn("reports/coverage.json", result["metric_files"])
        self.assertIn("browser_preview", {item["reader"] for item in result["reader_results"]})
        self.assertIn("log_artifact", {item["reader"] for item in result["reader_results"]})
        self.assertIn("metric_artifact", {item["reader"] for item in result["reader_results"]})
        self.assertTrue(
            any(item["kind"] == "preview" and item["path"] == "examples/web-game/index.html" for item in result["artifact_summaries"])
        )
        self.assertTrue(any(item["kind"] == "log" and item["path"] == "logs/agent.log" for item in result["artifact_summaries"]))
        self.assertTrue(
            any(item["kind"] == "metric" and item["path"] == "reports/coverage.json" for item in result["artifact_summaries"])
        )

    def test_returns_empty_snapshot_when_no_artifacts_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            (repo_path / "src").mkdir()
            (repo_path / "src" / "main.py").write_text("print('hi')\n", encoding="utf-8")

            result = ApplicationLegibilityCollector().collect(repo_path)

        self.assertFalse(result["available"])
        self.assertEqual(result["preview_targets"], [])
        self.assertEqual(result["log_files"], [])
        self.assertEqual(result["metric_files"], [])
        self.assertEqual(result["artifact_summaries"], [])
        self.assertEqual(len(result["reader_results"]), 3)


if __name__ == "__main__":
    unittest.main()
