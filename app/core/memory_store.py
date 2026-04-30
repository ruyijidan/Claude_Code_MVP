from __future__ import annotations

import json
import re
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

    def search_related(
        self,
        query: str,
        repo_path: Path,
        *,
        task_name: str | None = None,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        repo_path_str = str(repo_path)
        query_tokens = self._meaningful_tokens(query)
        matches: list[tuple[int, dict[str, Any]]] = []
        for payload in self.read_recent(limit=50):
            if payload.get("request_repo_path") != repo_path_str:
                continue
            score = self._score_payload(payload, query_tokens, task_name=task_name)
            if score <= 0:
                continue
            matches.append((score, self._summarize_payload(payload, score)))
        matches.sort(key=lambda item: (-item[0], item[1].get("request_prompt", "")))
        return [payload for _, payload in matches[:limit]]

    def _ensure_writable_root(self, root: Path) -> Path:
        try:
            root.mkdir(parents=True, exist_ok=True)
            return root
        except OSError:
            fallback = Path(tempfile.gettempdir()) / "claude_code_mvp" / root.name
            fallback.mkdir(parents=True, exist_ok=True)
            return fallback

    def _score_payload(self, payload: dict[str, Any], query_tokens: set[str], *, task_name: str | None) -> int:
        score = 0
        request_prompt = str(payload.get("request_prompt", ""))
        prompt_tokens = self._meaningful_tokens(request_prompt)
        changed_files = payload.get("changed_files", [])
        changed_paths = {str(path).lower() for path in changed_files if isinstance(path, str)}
        if task_name and payload.get("task") == task_name:
            score += 2
        overlap = query_tokens & prompt_tokens
        score += len(overlap) * 3
        for token in query_tokens:
            if any(token in path for path in changed_paths):
                score += 2
        if query_tokens and query_tokens <= prompt_tokens:
            score += 2
        return score

    def _summarize_payload(self, payload: dict[str, Any], score: int) -> dict[str, Any]:
        changed_files = payload.get("changed_files", [])
        return {
            "score": score,
            "task": payload.get("task"),
            "workflow": payload.get("workflow"),
            "request_prompt": payload.get("request_prompt"),
            "changed_files": changed_files[:5] if isinstance(changed_files, list) else [],
            "test_result": payload.get("test_result"),
            "completed_at": payload.get("completed_at"),
            "trajectory_path": payload.get("trajectory_path"),
        }

    def _meaningful_tokens(self, text: str) -> set[str]:
        tokens = re.findall(r"[a-zA-Z_]{3,}", text.lower())
        stopwords = {
            "the",
            "and",
            "for",
            "with",
            "this",
            "that",
            "from",
            "into",
            "write",
            "tests",
            "test",
            "add",
            "fix",
            "bug",
            "issue",
        }
        return {token for token in tokens if token not in stopwords}
