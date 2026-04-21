from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any


class MemoryStore:
    def __init__(self, root: Path) -> None:
        self.root = self._ensure_writable_root(root)

    def write(self, name: str, payload: dict[str, Any]) -> Path:
        path = self.root / f"{name}.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def read_latest(self) -> dict[str, Any] | None:
        candidates = sorted(self.root.glob("*.json"))
        if not candidates:
            return None
        latest = candidates[-1]
        try:
            return json.loads(latest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def read_recent(self, limit: int = 5) -> list[dict[str, Any]]:
        candidates = sorted(self.root.glob("*.json"))
        payloads: list[dict[str, Any]] = []
        for path in reversed(candidates[-limit:]):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(payload, dict):
                payloads.append(payload)
        return payloads

    def _ensure_writable_root(self, root: Path) -> Path:
        try:
            root.mkdir(parents=True, exist_ok=True)
            return root
        except OSError:
            fallback = Path(tempfile.gettempdir()) / "claude_code_mvp" / root.name
            fallback.mkdir(parents=True, exist_ok=True)
            return fallback
