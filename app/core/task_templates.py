from __future__ import annotations

from pathlib import Path


def _halo_drift_long_task_module_content() -> str:
    repo_root = Path(__file__).resolve().parents[2]
    game_path = repo_root / "examples" / "halo-drift" / "game.js"
    if game_path.exists():
        content = game_path.read_text(encoding="utf-8")
    else:
        content = ""

    replacements = [
        ("校准环轨，准备跃入星环", "校准环轨，进入长任务漂移"),
        (
            "收集发光回声点，避开暗色噪点。每次充能满格后，核心会进入下一阶段。",
            "收集发光回声点，避开暗色噪点。长任务会持续给出升级选择，帮助你把这局跑得更久。",
        ),
        (
            "马拉松模式会持续推进，并在每个阶段后给你一次永久升级选择。",
            "马拉松模式会持续推进，并在每个阶段后给你一次永久升级选择，适合 30 分钟长任务验证。",
        ),
        ("星环完成同步", "长任务同步完成"),
        ("轨道被噪点击穿", "长任务还没跑满"),
    ]
    for old, new in replacements:
        content = content.replace(old, new)

    banner = "// Long-task browser mini-game baseline for autonomous reruns.\n"
    if banner.strip() not in content:
        content = banner + content
    return content


def build_task_artifacts(task_name: str) -> dict[str, str]:
    if task_name == "long_task_game":
        return {
            "module_path": "examples/halo-drift/game.js",
            "module_content": _halo_drift_long_task_module_content(),
            "test_path": "tests/test_halo_drift_game.py",
            "test_content": """import unittest
from pathlib import Path


class HaloDriftGameTests(unittest.TestCase):
    def test_game_script_mentions_long_task_mode(self) -> None:
        game_script = Path("examples/halo-drift/game.js")
        self.assertTrue(game_script.exists())
        text = game_script.read_text(encoding="utf-8")
        self.assertIn("长任务", text)


if __name__ == "__main__":
    unittest.main()
""",
            "summary": "Updated the halo-drift browser game baseline for long-task reruns.",
        }

    if task_name == "fix_bug":
        return {
            "module_path": "app/calculator.py",
            "module_content": """from __future__ import annotations


def divide(left: float, right: float) -> float:
    if right == 0:
        raise ValueError("cannot divide by zero")
    return left / right
""",
            "test_path": "tests/test_calculator.py",
            "test_content": """import unittest

from app.calculator import divide


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
            "module_path": "app/string_utils.py",
            "module_content": """from __future__ import annotations


def slugify(value: str) -> str:
    return "-".join(value.lower().split())
""",
            "test_path": "tests/test_string_utils.py",
            "test_content": """import unittest

from app.string_utils import slugify


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
        "module_path": "app/tool_router.py",
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

from app.tool_router import ToolRouter


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
