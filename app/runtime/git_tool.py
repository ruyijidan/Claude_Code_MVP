from __future__ import annotations

from pathlib import Path

from app.runtime.ecc_adapter import ECCAdapter


class GitTool:
    def __init__(self, adapter: ECCAdapter | None = None) -> None:
        self.adapter = adapter or ECCAdapter()

    def status(self, repo_path: Path) -> dict:
        if not self._is_git_repo(repo_path):
            return {"available": False, "summary": "not a git repository"}

        code, output = self.adapter.run_command(["git", "status", "--short"], repo_path)
        return {
            "available": code == 0,
            "summary": output or "clean working tree",
            "is_clean": code == 0 and not output.strip(),
        }

    def branch(self, repo_path: Path) -> dict:
        if not self._is_git_repo(repo_path):
            return {"available": False, "name": None}

        code, output = self.adapter.run_command(["git", "branch", "--show-current"], repo_path)
        return {
            "available": code == 0,
            "name": output.strip() or None,
        }

    def diff(self, repo_path: Path) -> dict:
        if not self._is_git_repo(repo_path):
            return {"available": False, "summary": "not a git repository"}

        code, output = self.adapter.run_command(["git", "diff", "--", "."], repo_path)
        return {
            "available": code == 0,
            "summary": output.strip() or "no unstaged diff",
        }

    def changed_files(self, repo_path: Path) -> dict:
        if not self._is_git_repo(repo_path):
            return {"available": False, "files": []}

        diff_code, diff_output = self.adapter.run_command(["git", "diff", "--name-only", "--", "."], repo_path)
        status_code, status_output = self.adapter.run_command(["git", "status", "--short"], repo_path)
        if diff_code != 0 or status_code != 0:
            return {"available": False, "files": []}

        files: list[str] = []
        for line in diff_output.splitlines():
            value = line.strip()
            if value and value not in files:
                files.append(value)

        for line in status_output.splitlines():
            if not line.strip():
                continue
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                continue
            path = parts[1].strip()
            if " -> " in path:
                path = path.split(" -> ", maxsplit=1)[1].strip()
            if path and path not in files:
                files.append(path)

        return {
            "available": True,
            "files": files,
        }

    def diff_stats(self, repo_path: Path) -> dict:
        if not self._is_git_repo(repo_path):
            return {"available": False, "files": []}

        code, output = self.adapter.run_command(["git", "diff", "--numstat", "--", "."], repo_path)
        if code != 0:
            return {"available": False, "files": []}

        files: list[dict] = []
        total_added = 0
        total_deleted = 0
        for line in output.splitlines():
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            added_raw, deleted_raw, path = parts
            added = int(added_raw) if added_raw.isdigit() else 0
            deleted = int(deleted_raw) if deleted_raw.isdigit() else 0
            total_added += added
            total_deleted += deleted
            files.append({"path": path, "added": added, "deleted": deleted})
        return {
            "available": True,
            "files": files,
            "total_added": total_added,
            "total_deleted": total_deleted,
        }

    def review_summary(self, repo_path: Path) -> dict:
        if not self._is_git_repo(repo_path):
            return {"available": False, "summary": "not a git repository"}

        changed_files = self.changed_files(repo_path)
        stats = self.diff_stats(repo_path)
        if not changed_files.get("files"):
            return {
                "available": True,
                "summary": "No unstaged changes to review.",
                "files": [],
                "stats": stats,
            }

        file_count = len(changed_files["files"])
        total_added = stats.get("total_added", 0)
        total_deleted = stats.get("total_deleted", 0)
        top_files = ", ".join(changed_files["files"][:5])
        summary = (
            f"{file_count} file(s) changed, +{total_added}/-{total_deleted} lines. "
            f"Top files: {top_files}"
        )
        return {
            "available": True,
            "summary": summary,
            "files": changed_files["files"],
            "stats": stats,
        }

    def latest_commit_summary(self, repo_path: Path) -> dict:
        if not self._is_git_repo(repo_path):
            return {"available": False, "summary": None}

        code, output = self.adapter.run_command(["git", "log", "-1", "--pretty=%h %s"], repo_path)
        return {
            "available": code == 0,
            "summary": output.strip() or None,
        }

    def suggested_commit_message(self, repo_path: Path) -> dict:
        if not self._is_git_repo(repo_path):
            return {"available": False, "summary": None, "title": None}

        review = self.review_summary(repo_path)
        files = review.get("files", [])
        if not files:
            return {
                "available": True,
                "title": "chore: no working tree changes",
                "summary": "No unstaged changes detected, so no commit message is suggested.",
            }

        primary = self._infer_commit_subject(files)
        title = f"{primary}: update {self._format_scope(files)}"
        summary = review.get("summary", "")
        return {
            "available": True,
            "title": title,
            "summary": summary,
        }

    def snapshot(self, repo_path: Path) -> dict:
        status = self.status(repo_path)
        branch = self.branch(repo_path)
        diff = self.diff(repo_path)
        changed_files = self.changed_files(repo_path)
        review = self.review_summary(repo_path)
        latest_commit = self.latest_commit_summary(repo_path)
        suggested_commit = self.suggested_commit_message(repo_path)
        return {
            "available": status.get("available", False),
            "status": status,
            "branch": branch,
            "diff": diff,
            "changed_files": changed_files,
            "review": review,
            "latest_commit": latest_commit,
            "suggested_commit": suggested_commit,
        }

    def _is_git_repo(self, repo_path: Path) -> bool:
        return (repo_path / ".git").exists()

    def _infer_commit_subject(self, files: list[str]) -> str:
        joined = " ".join(files).lower()
        if "readme" in joined or joined.endswith(".md"):
            return "docs"
        if "app/" in joined or "cli" in joined or "runtime" in joined:
            return "feat"
        if "test" in joined:
            return "test"
        if "cli" in joined:
            return "feat"
        return "chore"

    def _format_scope(self, files: list[str]) -> str:
        first = files[0]
        top = first.split("/", maxsplit=1)[0]
        if len(files) == 1:
            return first
        return top
