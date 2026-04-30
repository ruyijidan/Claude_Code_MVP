from __future__ import annotations

import unittest
from pathlib import Path

from app.agent.workflow_executor import WorkflowExecutor
from app.core.spec_loader import SpecLoader
from app.core.tool_registry import ToolRegistry
from app.runtime.artifact_readers import ArtifactReaderRegistry, BrowserPreviewReader, LogArtifactReader, MetricArtifactReader


class WorkflowExecutorTests(unittest.TestCase):
    def _build_executor(self) -> WorkflowExecutor:
        root = Path(__file__).resolve().parents[1] / "specs"
        loader = SpecLoader(root)
        tool_registry = ToolRegistry(loader.load_tools())
        reader_registry = ArtifactReaderRegistry(loader.load_readers())
        reader_registry.register(BrowserPreviewReader())
        reader_registry.register(LogArtifactReader())
        reader_registry.register(MetricArtifactReader())
        return WorkflowExecutor(tool_registry, reader_registry)

    def test_begin_records_selected_tools_and_readers(self) -> None:
        root = Path(__file__).resolve().parents[1] / "specs"
        loader = SpecLoader(root)
        executor = self._build_executor()
        task = loader.load_task("implement_feature")
        workflow = loader.load_workflow("implement-feature")

        result = executor.begin(
            task,
            workflow,
            {
                "application_legibility": {
                    "reader_results": [
                        {"reader": "browser_preview", "paths": ["examples/web/index.html"]},
                        {"reader": "log_artifact", "paths": ["logs/agent.log"]},
                        {"reader": "metric_artifact", "paths": []},
                    ]
                }
            },
            [{"id": "workflow_context"}, {"id": "workflow_step_1"}],
        )

        self.assertEqual(result["status"], "running")
        self.assertIn("file_tool", {item["name"] for item in result["selected_tools"]})
        self.assertIn("browser_preview", {item["name"] for item in result["selected_readers"]})
        self.assertIn("log_artifact", {item["name"] for item in result["selected_readers"]})

    def test_complete_marks_workflow_status(self) -> None:
        executor = self._build_executor()
        result = executor.complete(
            {
                "selected_path": "complete",
                "critic_issues": [],
                "workflow_execution": {
                    "steps": [
                        {"id": "workflow_step_1", "description": "a", "status": "pending"},
                        {"id": "workflow_step_2", "description": "b", "status": "pending"},
                    ]
                },
            }
        )

        self.assertEqual(result["workflow_execution"]["status"], "completed")
        self.assertTrue(all(step["status"] == "completed" for step in result["workflow_execution"]["steps"]))


if __name__ == "__main__":
    unittest.main()
