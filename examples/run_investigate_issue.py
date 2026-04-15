from __future__ import annotations

import json
from pathlib import Path

from app.main import run_task


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    workspace = root / "workspace_investigate"
    workspace.mkdir(exist_ok=True)
    result = run_task(workspace, "investigate_issue", "Investigate intermittent tool routing failures")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
