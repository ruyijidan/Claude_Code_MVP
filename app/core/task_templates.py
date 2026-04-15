from __future__ import annotations


def build_task_artifacts(task_name: str) -> dict[str, str]:
    if task_name == "fix_bug":
        return {
            "module_path": "sample_app/calculator.py",
            "module_content": """from __future__ import annotations


def divide(left: float, right: float) -> float:
    if right == 0:
        raise ValueError("cannot divide by zero")
    return left / right
""",
            "test_path": "tests/test_calculator.py",
            "test_content": """import unittest

from sample_app.calculator import divide


class CalculatorTests(unittest.TestCase):
    def test_divide_returns_quotient(self) -> None:
        self.assertEqual(divide(8, 2), 4)

    def test_divide_rejects_zero_divisor(self) -> None:
        with self.assertRaises(ValueError):
            divide(1, 0)


if __name__ == "__main__":
    unittest.main()
""",
            "summary": "Implemented a safe calculator divide function and regression tests.",
        }

    if task_name == "write_tests":
        return {
            "module_path": "sample_app/string_utils.py",
            "module_content": """from __future__ import annotations


def slugify(value: str) -> str:
    return "-".join(value.lower().split())
""",
            "test_path": "tests/test_string_utils.py",
            "test_content": """import unittest

from sample_app.string_utils import slugify


class StringUtilsTests(unittest.TestCase):
    def test_slugify_lowercases_and_joins_words(self) -> None:
        self.assertEqual(slugify("Hello Spec Coding"), "hello-spec-coding")


if __name__ == "__main__":
    unittest.main()
""",
            "summary": "Added a sample utility module and test coverage for slugification.",
        }

    if task_name == "investigate_issue":
        return {
            "module_path": "reports/investigation.md",
            "module_content": """# Investigation Report

- Symptom: Intermittent tool routing failures under missing registrations.
- Likely cause: Callers resolve tool names before populating the registry.
- Suggested fix: Add a verifier check for missing tool setup before execution.
""",
            "test_path": "tests/test_investigation_report.py",
            "test_content": """import unittest
from pathlib import Path


class InvestigationReportTests(unittest.TestCase):
    def test_report_is_generated(self) -> None:
        report = Path("reports/investigation.md")
        self.assertTrue(report.exists())
        self.assertIn("Likely cause", report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
""",
            "summary": "Generated an investigation report and a guard test that verifies it exists.",
        }

    return {
        "module_path": "sample_app/tool_router.py",
        "module_content": """from __future__ import annotations


class ToolRouter:
    def __init__(self) -> None:
        self._routes: dict[str, str] = {}

    def register(self, tool_name: str, handler: str) -> None:
        self._routes[tool_name] = handler

    def resolve(self, tool_name: str) -> str:
        if tool_name not in self._routes:
            raise KeyError(f"unknown tool: {tool_name}")
        return self._routes[tool_name]
""",
        "test_path": "tests/test_tool_router.py",
        "test_content": """import unittest

from sample_app.tool_router import ToolRouter


class ToolRouterTests(unittest.TestCase):
    def test_register_and_resolve(self) -> None:
        router = ToolRouter()
        router.register("shell", "shell_handler")
        self.assertEqual(router.resolve("shell"), "shell_handler")

    def test_unknown_tool_raises(self) -> None:
        router = ToolRouter()
        with self.assertRaises(KeyError):
            router.resolve("missing")


if __name__ == "__main__":
    unittest.main()
""",
        "summary": "Implemented a basic tool router and coverage for the core routing behavior.",
    }
