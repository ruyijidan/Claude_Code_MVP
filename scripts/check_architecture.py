from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

RULES = [
    {
        "source": ROOT / "app" / "runtime",
        "forbidden": ["app.cli", "app.agent"],
        "message": (
            "❌ app/runtime must not depend on app.cli or app.agent.\n"
            "✅ FIX: move orchestration logic upward into app/agent or app/cli.\n"
            "📖 See: docs/architecture/boundaries.md"
        ),
    },
    {
        "source": ROOT / "app" / "agent",
        "forbidden": ["app.cli"],
        "message": (
            "❌ app/agent must not depend on app.cli.\n"
            "✅ FIX: keep agent logic presentation-agnostic and let CLI call into the agent layer.\n"
            "📖 See: docs/architecture/boundaries.md"
        ),
    },
]

SIZE_RULES = [
    {
        "path": ROOT / "app" / "cli" / "main.py",
        "max_lines": 380,
        "message": (
            "❌ app/cli/main.py is too large for the CLI control surface.\n"
            "✅ FIX: move reusable behavior into app/agent, app/core, or app/runtime helpers.\n"
            "📖 See: docs/architecture/boundaries.md"
        ),
    },
    {
        "path": ROOT / "app" / "acceptance" / "report_runner.py",
        "max_lines": 220,
        "message": (
            "❌ app/acceptance/report_runner.py is growing beyond a review-friendly size.\n"
            "✅ FIX: split prompt building, retry policy, or result shaping into helpers.\n"
            "📖 See: docs/architecture/boundaries.md"
        ),
    },
]


def iter_python_files(directory: Path) -> list[Path]:
    return [
        path
        for path in directory.rglob("*.py")
        if "__pycache__" not in path.parts
    ]


def find_import_violations(root: Path) -> list[str]:
    violations: list[str] = []
    for rule in RULES:
        source = rule["source"]
        for file_path in iter_python_files(source):
            text = file_path.read_text(encoding="utf-8")
            for forbidden in rule["forbidden"]:
                if f"from {forbidden} " in text or f"import {forbidden}" in text:
                    violations.append(f"{file_path.relative_to(root)}\n{rule['message']}")
    return violations


def find_size_violations(root: Path) -> list[str]:
    violations: list[str] = []
    for rule in SIZE_RULES:
        file_path = rule["path"]
        if not file_path.exists():
            continue
        with file_path.open("r", encoding="utf-8") as handle:
            line_count = sum(1 for _ in handle)
        if line_count > rule["max_lines"]:
            violations.append(
                f"{file_path.relative_to(root)} ({line_count} lines > {rule['max_lines']})\n{rule['message']}"
            )
    return violations


def main() -> int:
    violations = find_import_violations(ROOT) + find_size_violations(ROOT)

    if violations:
        print("\n\n".join(violations))
        return 1

    print("✅ Architecture boundary and size checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
