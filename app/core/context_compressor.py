from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class ContextBudget:
    max_prompt_chars: int = 320
    max_file_chars: int = 240
    max_candidate_files: int = 12
    max_relevant_files: int = 8
    max_test_targets: int = 6
    max_path_chars: int = 320
    max_git_status_lines: int = 8
    max_git_diff_lines: int = 8
    max_git_chars: int = 800

    def to_dict(self) -> dict:
        return asdict(self)


def summarize_text(text: str, *, max_chars: int) -> str:
    normalized = text.strip()
    if len(normalized) <= max_chars:
        return normalized
    head_budget = max_chars // 2
    tail_budget = max_chars - head_budget - len("\n...\n")
    head = normalized[:head_budget].rstrip()
    tail = normalized[-tail_budget:].lstrip()
    return f"{head}\n...\n{tail}"


def summarize_lines(lines: list[str], *, max_items: int, max_chars: int) -> str:
    selected = [line.strip() for line in lines if line.strip()]
    if not selected:
        return ""
    if len(selected) > max_items:
        hidden_count = len(selected) - max_items
        selected = selected[:max_items] + [f"... ({hidden_count} more lines)"]
    return summarize_text("\n".join(selected), max_chars=max_chars)


def summarize_paths(paths: list[str], *, max_items: int, max_chars: int) -> str:
    return summarize_lines(paths, max_items=max_items, max_chars=max_chars)
