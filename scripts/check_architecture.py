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


def iter_python_files(directory: Path) -> list[Path]:
    return [
        path
        for path in directory.rglob("*.py")
        if "__pycache__" not in path.parts
    ]


def main() -> int:
    violations: list[str] = []

    for rule in RULES:
        for file_path in iter_python_files(rule["source"]):
            text = file_path.read_text(encoding="utf-8")
            for forbidden in rule["forbidden"]:
                if f"from {forbidden} " in text or f"import {forbidden}" in text:
                    violations.append(f"{file_path.relative_to(ROOT)}\n{rule['message']}")

    if violations:
        print("\n\n".join(violations))
        return 1

    print("✅ Architecture boundary checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
