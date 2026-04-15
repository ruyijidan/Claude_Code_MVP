from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.agent.loop import CodingAgentLoop
from app.agent.policies import ExecutionPolicy, PermissionPipeline
from app.core.env_loader import load_project_env
from app.core.memory_store import MemoryStore
from app.core.spec_loader import SpecLoader
from app.runtime.adapter_factory import build_runtime_adapter
from app.runtime.git_tool import GitTool


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cc", description="Claude Code MVP CLI")
    parser.add_argument("prompt", nargs="?", default="", help='Developer request, for example: cc "fix failing tests"')
    parser.add_argument("--repo", default=".", help="Repository path to operate on")
    parser.add_argument("--provider", default=None, help="Runtime provider: local, claude_code, codex_cli")
    parser.add_argument("--task-type", default=None, help="Optional explicit task type override")
    parser.add_argument("--json", action="store_true", help="Print full JSON result")
    parser.add_argument("--show-status", action="store_true", help="Show git status before running")
    parser.add_argument("--show-diff", action="store_true", help="Show git diff before running")
    parser.add_argument("--show-changed-files", action="store_true", help="Show changed files before running")
    parser.add_argument("--show-review", action="store_true", help="Show diff stats and a review summary before running")
    parser.add_argument("--show-commit-summary", action="store_true", help="Show a suggested commit message before running")
    parser.add_argument("--show-permissions", action="store_true", help="Show permission decisions before running")
    parser.add_argument(
        "--show-post-review",
        action="store_true",
        help="Show changed files and a review summary after a successful local loop run",
    )
    parser.add_argument(
        "--show-post-commit-summary",
        action="store_true",
        help="Show a suggested commit message after a successful local loop run",
    )
    parser.add_argument(
        "--delegate-to-provider",
        action="store_true",
        help="Use the selected external provider CLI directly when available",
    )
    parser.add_argument("--auto-approve", action="store_true", help="Skip confirmation steps")
    parser.add_argument(
        "--dangerously-skip-confirmation",
        action="store_true",
        help="Bypass confirmation prompts for unattended runs",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    repo_path = Path(args.repo).resolve()
    load_project_env(repo_path)
    spec_root = Path(__file__).resolve().parents[2] / "specs"
    loader = SpecLoader(spec_root)
    adapter = build_runtime_adapter(args.provider)
    provider_info = adapter.provider_info()
    git_tool = GitTool(adapter)
    policy = ExecutionPolicy(
        auto_approve=bool(args.auto_approve),
        dangerously_skip_confirmation=bool(args.dangerously_skip_confirmation),
    )
    permission_pipeline = PermissionPipeline()

    if not args.prompt and not (
        args.show_status or args.show_diff or args.show_changed_files or args.show_review or args.show_commit_summary or args.show_permissions
    ):
        parser.error("a prompt is required unless a git inspection flag is used")

    if args.show_permissions:
        inspect_decision = permission_pipeline.assess("inspect", policy, provider_info=provider_info)
        if args.json:
            print(json.dumps({"permissions": inspect_decision.to_dict()}, indent=2))
        else:
            print("permissions:")
            print(json.dumps(inspect_decision.to_dict(), indent=2))

    if args.show_status:
        status = git_tool.status(repo_path)
        if args.json:
            print(json.dumps({"git_status": status}, indent=2))
        else:
            print("git status:")
            print(status.get("summary"))

    if args.show_diff:
        diff = git_tool.diff(repo_path)
        if args.json:
            print(json.dumps({"git_diff": diff}, indent=2))
        else:
            print("git diff:")
            print(diff.get("summary"))

    if args.show_changed_files:
        changed_files = git_tool.changed_files(repo_path)
        if args.json:
            print(json.dumps({"git_changed_files": changed_files}, indent=2))
        else:
            print("changed files:")
            files = changed_files.get("files", [])
            print("\n".join(files) if files else "no unstaged changed files")

    if args.show_review:
        review = git_tool.review_summary(repo_path)
        if args.json:
            print(json.dumps({"git_review": review}, indent=2))
        else:
            print("git review:")
            print(review.get("summary"))
            for item in review.get("stats", {}).get("files", [])[:10]:
                print(f"{item['path']}: +{item['added']} -{item['deleted']}")

    if args.show_commit_summary:
        commit_summary = git_tool.suggested_commit_message(repo_path)
        if args.json:
            print(json.dumps({"git_commit_summary": commit_summary}, indent=2))
        else:
            print("suggested commit:")
            print(commit_summary.get("title"))
            print(commit_summary.get("summary"))
    if not args.prompt:
        return 0

    if args.delegate_to_provider:
        permission = permission_pipeline.assess("delegated_provider", policy, provider_info=provider_info)
        if not permission.approved:
            payload = {
                "error": "permission_denied",
                "permission": permission.to_dict(),
            }
            if args.json:
                print(json.dumps(payload, indent=2))
            else:
                print(f"provider: {adapter.provider_name}")
                print("mode: delegated_provider")
                print("status: blocked")
                print(permission.reason)
                if permission.recommended_flag:
                    print(f"hint: retry with {permission.recommended_flag} if you trust this environment")
            return 1

        if not adapter.can_delegate_prompt():
            print(json.dumps({"error": "provider does not support delegated prompt execution", "provider_info": provider_info}, indent=2))
            return 1

        code, output, command = adapter.execute_prompt(
            args.prompt,
            repo_path,
            auto_approve=bool(args.auto_approve or args.dangerously_skip_confirmation),
        )
        if args.json:
            print(
                json.dumps(
                    {
                        "mode": "delegated_provider",
                        "provider": adapter.provider_name,
                        "provider_info": provider_info,
                        "permission": permission.to_dict(),
                        "command": command,
                        "returncode": code,
                        "output": output,
                    },
                    indent=2,
                )
            )
        else:
            print(f"provider: {adapter.provider_name}")
            print("mode: delegated_provider")
            print(f"risk: {permission.risk}")
            print(f"available: {provider_info['available']}")
            print(f"returncode: {code}")
            print(output)
        return 0 if code == 0 else code

    permission = permission_pipeline.assess("local_loop", policy, provider_info=provider_info)
    loop = CodingAgentLoop(
        spec_loader=loader,
        memory_store=MemoryStore(repo_path / ".claude-code" / "trajectories"),
        adapter=adapter,
    )
    try:
        result = loop.run(repo_path=repo_path, prompt=args.prompt, task_name=args.task_type)
    except OSError as exc:
        payload = {
            "error": "local_loop_failed",
            "message": str(exc),
            "hint": "Make sure the target repository is writable, or use --delegate-to-provider.",
            "provider": adapter.provider_name,
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"provider: {adapter.provider_name}")
            print("mode: local_loop")
            print(f"risk: {permission.risk}")
            print("status: failed")
            print(payload["message"])
            print(payload["hint"])
        return 1

    if args.json:
        result = {
            **result,
            "permission": permission.to_dict(),
        }
        if args.show_post_review:
            post_review = git_tool.review_summary(repo_path)
            post_changed_files = git_tool.changed_files(repo_path)
            result = {
                **result,
                "post_review": post_review,
                "post_changed_files": post_changed_files,
            }
        if args.show_post_commit_summary:
            result = {
                **result,
                "post_commit_summary": git_tool.suggested_commit_message(repo_path),
            }
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"provider: {result['runtime_provider']}")
        print("mode: local_loop")
        print(f"risk: {permission.risk}")
        print(f"task: {result['task_spec'].name}")
        print(f"status: {result['test_result']}")
        print(f"changed_files: {len(result.get('changed_files', []))}")
        git_snapshot = result.get("repo_context", {}).get("git", {})
        branch_name = git_snapshot.get("branch", {}).get("name")
        if branch_name:
            print(f"branch: {branch_name}")
        if args.show_post_review:
            post_review = git_tool.review_summary(repo_path)
            post_changed_files = git_tool.changed_files(repo_path)
            print("post changed files:")
            files = post_changed_files.get("files", [])
            print("\n".join(files) if files else "no unstaged changed files")
            print("post review:")
            print(post_review.get("summary"))
            for item in post_review.get("stats", {}).get("files", [])[:10]:
                print(f"{item['path']}: +{item['added']} -{item['deleted']}")
        if args.show_post_commit_summary:
            post_commit_summary = git_tool.suggested_commit_message(repo_path)
            print("post commit summary:")
            print(post_commit_summary.get("title"))
            print(post_commit_summary.get("summary"))
        print(f"trajectory: {result['trajectory_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
