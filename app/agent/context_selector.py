from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(slots=True)
class ScopedContext:
    repo_path: str
    prompt: str
    git_summary: dict
    always_include_docs: list[str]
    likely_relevant_files: list[str]
    test_targets: list[str]
    architecture_constraints: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


class ContextSelector:
    ALWAYS_INCLUDE_DOCS = [
        "AGENTS.md",
        "ARCHITECTURE.md",
        "docs/architecture/boundaries.md",
    ]

    def select(self, repo_path: Path, prompt: str, git_summary: dict, candidate_files: list[str]) -> ScopedContext:
        prompt_tokens = self._tokenize(prompt)
        likely_relevant_files = self._select_relevant_files(candidate_files, prompt_tokens)
        test_targets = self._select_test_targets(candidate_files, prompt_tokens)
        architecture_constraints = [
            path for path in self.ALWAYS_INCLUDE_DOCS if "boundaries" in path or "AGENTS.md" in path
        ]
        return ScopedContext(
            repo_path=str(repo_path),
            prompt=prompt,
            git_summary=git_summary,
            always_include_docs=[path for path in self.ALWAYS_INCLUDE_DOCS if (repo_path / path).exists()],
            likely_relevant_files=likely_relevant_files,
            test_targets=test_targets,
            architecture_constraints=architecture_constraints,
        )

    def _select_relevant_files(self, candidate_files: list[str], prompt_tokens: set[str]) -> list[str]:
        matched: list[str] = []
        fallback: list[str] = []
        for path in candidate_files:
            normalized = path.lower()
            if self._is_test_file(normalized):
                continue
            fallback.append(path)
            if any(token in normalized for token in prompt_tokens):
                matched.append(path)
        selected = matched or fallback
        return selected[:8]

    def _select_test_targets(self, candidate_files: list[str], prompt_tokens: set[str]) -> list[str]:
        matched: list[str] = []
        tests = [path for path in candidate_files if self._is_test_file(path.lower())]
        for path in tests:
            normalized = path.lower()
            if any(token in normalized for token in prompt_tokens):
                matched.append(path)
        return (matched or tests)[:6]

    def _is_test_file(self, path: str) -> bool:
        return path.startswith("tests/") or "/tests/" in path or path.rsplit("/", maxsplit=1)[-1].startswith("test_")

    def _tokenize(self, prompt: str) -> set[str]:
        cleaned = []
        for char in prompt.lower():
            cleaned.append(char if char.isalnum() else " ")
        tokens = {token for token in "".join(cleaned).split() if len(token) >= 3}
        return tokens
