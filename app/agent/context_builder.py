from __future__ import annotations

from pathlib import Path

from app.runtime.ecc_adapter import ECCAdapter
from app.runtime.git_tool import GitTool


class RepoContextBuilder:
    def __init__(self, adapter: ECCAdapter | None = None) -> None:
        self.adapter = adapter or ECCAdapter()
        self.git_tool = GitTool(self.adapter)

    def build(self, repo_path: Path, prompt: str) -> dict:
        files = self._sample_files(repo_path)
        git_summary = self.git_tool.snapshot(repo_path)
        return {
            "repo_path": str(repo_path),
            "prompt": prompt,
            "git": git_summary,
            "candidate_files": files,
            "has_tests": (repo_path / "tests").exists(),
        }

    def _sample_files(self, repo_path: Path) -> list[str]:
        candidates: list[str] = []
        for path in sorted(repo_path.rglob("*")):
            if len(candidates) >= 12:
                break
            if not path.is_file():
                continue
            if ".git" in path.parts or "__pycache__" in path.parts:
                continue
            candidates.append(str(path.relative_to(repo_path)))
        return candidates
