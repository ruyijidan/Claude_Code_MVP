from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.agent.context_selector import ContextSelector


class ContextSelectorTests(unittest.TestCase):
    def test_selects_docs_relevant_files_and_tests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            (repo_path / "docs" / "architecture").mkdir(parents=True)
            (repo_path / "AGENTS.md").write_text("# agents\n", encoding="utf-8")
            (repo_path / "ARCHITECTURE.md").write_text("# architecture\n", encoding="utf-8")
            (repo_path / "docs" / "architecture" / "boundaries.md").write_text("# boundaries\n", encoding="utf-8")

            selector = ContextSelector()
            result = selector.select(
                repo_path,
                "write tests for router",
                {"available": False},
                [
                    "sample_app/tool_router.py",
                    "sample_app/calculator.py",
                    "tests/test_tool_router.py",
                    "README.md",
                ],
            )

            self.assertIn("AGENTS.md", result.always_include_docs)
            self.assertIn("sample_app/tool_router.py", result.likely_relevant_files)
            self.assertIn("tests/test_tool_router.py", result.test_targets)
            self.assertIn("docs/architecture/boundaries.md", result.architecture_constraints)


if __name__ == "__main__":
    unittest.main()
