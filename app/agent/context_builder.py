from __future__ import annotations

from pathlib import Path

from app.agent.context_selector import ContextSelector
from app.core.context_compressor import ContextBudget, summarize_paths, summarize_text
from app.runtime.ecc_adapter import ECCAdapter
from app.runtime.git_tool import GitTool


class RepoContextBuilder:
    def __init__(self, adapter: ECCAdapter | None = None, budget: ContextBudget | None = None) -> None:
        self.adapter = adapter or ECCAdapter()
        self.git_tool = GitTool(self.adapter)
        self.budget = budget or ContextBudget()
        self.selector = ContextSelector(self.budget)

    def build(self, repo_path: Path, prompt: str) -> dict:
        files = self._sample_files(repo_path)
        git_summary = self.git_tool.snapshot(repo_path)
        scoped_context = self.selector.select(repo_path, prompt, git_summary, files)
        file_summaries = self._summarize_files(repo_path, scoped_context.likely_relevant_files)
        return {
            "repo_path": str(repo_path),
            "prompt": prompt,
            "prompt_summary": summarize_text(prompt, max_chars=self.budget.max_prompt_chars),
            "context_budget": self.budget.to_dict(),
            "git": git_summary,
            "git_summary_compact": self._compact_git_summary(git_summary),
            "candidate_files": files,
            "candidate_files_summary": summarize_paths(
                files,
                max_items=self.budget.max_candidate_files,
                max_chars=self.budget.max_path_chars,
            ),
            "has_tests": (repo_path / "tests").exists(),
            "always_include_docs": scoped_context.always_include_docs,
            "likely_relevant_files": scoped_context.likely_relevant_files,
            "likely_relevant_files_summary": summarize_paths(
                scoped_context.likely_relevant_files,
                max_items=self.budget.max_relevant_files,
                max_chars=self.budget.max_path_chars,
            ),
            "test_targets": scoped_context.test_targets,
            "test_targets_summary": summarize_paths(
                scoped_context.test_targets,
                max_items=self.budget.max_test_targets,
                max_chars=self.budget.max_path_chars,
            ),
            "architecture_constraints": scoped_context.architecture_constraints,
            "candidate_file_summaries": file_summaries,
            "scoped_context": scoped_context.to_dict(),
        }

    def _sample_files(self, repo_path: Path) -> list[str]:
        candidates: list[str] = []
        for path in sorted(repo_path.rglob("*")):
            if len(candidates) >= self.budget.max_candidate_files:
                break
            if not path.is_file():
                continue
            if ".git" in path.parts or "__pycache__" in path.parts:
                continue
            candidates.append(str(path.relative_to(repo_path)))
        return candidates

    def _summarize_files(self, repo_path: Path, paths: list[str]) -> list[dict[str, str]]:
        summaries: list[dict[str, str]] = []
        for relative_path in paths:
            file_path = repo_path / relative_path
            try:
                text = file_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            summaries.append(
                {
                    "path": relative_path,
                    "summary": summarize_text(text, max_chars=self.budget.max_file_chars),
                }
            )
        return summaries

    def _compact_git_summary(self, git_summary: dict) -> dict[str, str]:
        status_files = git_summary.get("changed_files", {}).get("files", [])
        diff_files = git_summary.get("changed_files", {}).get("files", [])
        return {
            "available": "yes" if git_summary.get("available") else "no",
            "branch": git_summary.get("branch", {}).get("name", ""),
            "status_summary": summarize_lines_from_paths(status_files, self.budget.max_git_status_lines, self.budget.max_git_chars),
            "diff_summary": summarize_lines_from_paths(diff_files, self.budget.max_git_diff_lines, self.budget.max_git_chars),
        }


def summarize_lines_from_paths(paths: list[str], max_items: int, max_chars: int) -> str:
    return summarize_paths(paths, max_items=max_items, max_chars=max_chars)
