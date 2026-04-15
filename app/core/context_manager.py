from __future__ import annotations

from pathlib import Path


class ContextManager:
    def build(self, repo_path: Path, task_payload: dict) -> dict:
        return {
            "repo_path": str(repo_path),
            "request": task_payload,
        }
