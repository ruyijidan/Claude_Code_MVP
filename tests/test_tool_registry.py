from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.core.spec_loader import SpecLoader
from app.core.tool_registry import ToolRegistry
from app.runtime.local_runtime import LocalRuntimeAdapter
from app.tools.file_tool import FileTool
from app.tools.test_tool import TestTool


class ToolRegistryTests(unittest.TestCase):
    def _loader(self) -> SpecLoader:
        root = Path(__file__).resolve().parents[1] / "specs"
        return SpecLoader(root)

    def test_file_tool_invoke_validates_schema(self) -> None:
        registry = ToolRegistry(self._loader().load_tools())
        registry.register(FileTool())

        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "sample.txt"
            target.write_text("hello\n", encoding="utf-8")
            result = registry.invoke("file_tool", path=str(target))

        self.assertEqual(result["path"], str(target))
        self.assertTrue(result["exists"])
        self.assertIn("hello", result["content"])

    def test_test_tool_invoke_validates_schema(self) -> None:
        registry = ToolRegistry(self._loader().load_tools())
        registry.register(TestTool(LocalRuntimeAdapter()))

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            (repo_path / "tests").mkdir()
            (repo_path / "tests" / "test_ok.py").write_text(
                "import unittest\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            result = registry.invoke("test_tool", repo_path=str(repo_path))

        self.assertEqual(result["returncode"], 0)
        self.assertIsInstance(result["output"], str)


if __name__ == "__main__":
    unittest.main()
