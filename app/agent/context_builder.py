from __future__ import annotations

from pathlib import Path

from app.agent.context_selector import ContextSelector
from app.runtime.ecc_adapter import ECCAdapter
from app.runtime.git_tool import GitTool


class RepoContextBuilder:
    def __init__(self, adapter: ECCAdapter | None = None) -> None:
        self.adapter = adapter or ECCAdapter()
        self.git_tool = GitTool(self.adapter)
        self.selector = ContextSelector()

    def build(self, repo_path: Path, prompt: str) -> dict:
        files = self._sample_files(repo_path)
        git_summary = self.git_tool.snapshot(repo_path)
        scoped_context = self.selector.select(repo_path, prompt, git_summary, files)
        return {
            "repo_path": str(repo_path),
            "prompt": prompt,
            "git": git_summary,
            "candidate_files": files,
            "has_tests": (repo_path / "tests").exists(),
            "always_include_docs": scoped_context.always_include_docs,
            "likely_relevant_files": scoped_context.likely_relevant_files,
            "test_targets": scoped_context.test_targets,
            "architecture_constraints": scoped_context.architecture_constraints,
            "scoped_context": scoped_context.to_dict(),
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
