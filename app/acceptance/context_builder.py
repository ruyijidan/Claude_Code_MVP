from __future__ import annotations

import subprocess
from pathlib import Path

from app.core.context_compressor import summarize_paths, summarize_text


MAX_DOC_CHARS = 2400
MAX_GIT_CHARS = 1200
MAX_GIT_FILES = 12
GIT_STATUS_SNAPSHOT_PATH = Path(".claude-code/acceptance/context/git_status.txt")
GIT_DIFF_STAT_SNAPSHOT_PATH = Path(".claude-code/acceptance/context/git_diff_stat.txt")


def _read_optional(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _run_git(repo_path: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return completed.stderr.strip() or completed.stdout.strip()
    return completed.stdout.strip()


def _load_git_snapshot(repo_path: Path, relative_path: Path) -> str:
    snapshot_path = repo_path / relative_path
    if not snapshot_path.exists():
        return ""
    return snapshot_path.read_text(encoding="utf-8").strip()

def _extract_changed_paths(text: str) -> list[str]:
    paths: list[str] = []
    for line in text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        if "|" in cleaned:
            paths.append(cleaned.split("|", maxsplit=1)[0].strip())
            continue
        if cleaned.startswith("?? "):
            paths.append(cleaned[3:].strip())
            continue
        if len(cleaned) > 2 and cleaned[1] == " " and cleaned[0] in {"M", "A", "D", "R", "C", "U"}:
            paths.append(cleaned[2:].strip())
    return paths


def build_acceptance_context(repo_path: Path) -> dict[str, str]:
    git_status = _run_git(repo_path, ["status", "--short"])
    git_diff_stat = _run_git(repo_path, ["diff", "--stat"])
    if "not a git repository" in git_status.lower():
        git_status = _load_git_snapshot(repo_path, GIT_STATUS_SNAPSHOT_PATH) or git_status
    if "not a git repository" in git_diff_stat.lower():
        git_diff_stat = _load_git_snapshot(repo_path, GIT_DIFF_STAT_SNAPSHOT_PATH) or git_diff_stat

    return {
        "readme": summarize_text(_read_optional(repo_path / "README.md"), max_chars=MAX_DOC_CHARS),
        "architecture": summarize_text(_read_optional(repo_path / "ARCHITECTURE.md"), max_chars=MAX_DOC_CHARS),
        "testing_conventions": summarize_text(
            _read_optional(repo_path / "docs" / "conventions" / "testing.md"),
            max_chars=MAX_DOC_CHARS,
        ),
        "current_sprint": summarize_text(
            _read_optional(repo_path / "docs" / "plans" / "current-sprint.md"),
            max_chars=MAX_DOC_CHARS,
        ),
        "release_notes": summarize_text(
            _read_optional(repo_path / "docs" / "plans" / "release-notes.md"),
            max_chars=MAX_DOC_CHARS,
        ),
        "git_status": summarize_text(git_status, max_chars=MAX_GIT_CHARS),
        "git_diff_stat": summarize_text(git_diff_stat, max_chars=MAX_GIT_CHARS),
        "git_status_paths": summarize_paths(
            _extract_changed_paths(git_status),
            max_items=MAX_GIT_FILES,
            max_chars=MAX_GIT_CHARS,
        ),
        "git_diff_paths": summarize_paths(
            _extract_changed_paths(git_diff_stat),
            max_items=MAX_GIT_FILES,
            max_chars=MAX_GIT_CHARS,
        ),
    }
