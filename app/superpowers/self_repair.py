from __future__ import annotations

from pathlib import Path

from app.core.task_templates import build_task_artifacts
from app.runtime.ecc_adapter import ECCAdapter


class SelfRepairEngine:
    def __init__(self, adapter: ECCAdapter | None = None) -> None:
        self.adapter = adapter or ECCAdapter()

    def repair(self, state: dict, issues: list[str]) -> dict:
        if not issues:
            return {"repair_action": "none"}

        repo_path = Path(state["repo_path"])
        artifacts = build_task_artifacts(state["task_spec"].name)
        test_file = repo_path / artifacts["test_path"]
        if not test_file.exists():
            self.adapter.edit_file(test_file, artifacts["test_content"])
            return {
                "repair_action": "added_missing_tests",
                "changed_files": state.get("changed_files", []) + [str(test_file)],
            }

        return {"repair_action": "no_op"}
