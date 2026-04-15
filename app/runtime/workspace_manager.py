from __future__ import annotations

from pathlib import Path


class WorkspaceManager:
    def ensure(self, path: Path) -> Path:
        path.mkdir(parents=True, exist_ok=True)
        return path
