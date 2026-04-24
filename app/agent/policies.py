from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

from app.core.models import PermissionRulesSpec


@dataclass(slots=True)
class ExecutionPolicy:
    auto_approve: bool = False
    dangerously_skip_confirmation: bool = False

    @property
    def mode(self) -> str:
        if self.dangerously_skip_confirmation:
            return "dangerous"
        if self.auto_approve:
            return "auto"
        return "default"

    def requires_confirmation(self) -> bool:
        return not (self.auto_approve or self.dangerously_skip_confirmation)


@dataclass(slots=True)
class PermissionDecision:
    operation: str
    policy_mode: str
    decision: str
    action: str
    risk: str
    approved: bool
    requires_confirmation: bool
    scope: str
    boundary: str
    reason: str
    recommended_flag: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class CommandPermissionDecision:
    command: list[str]
    command_text: str
    category: str
    policy_mode: str
    decision: str
    action: str
    risk: str
    approved: bool
    requires_confirmation: bool
    scope: str
    boundary: str
    reason: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class FileWriteDecision:
    path: str
    repo_root: str
    policy_mode: str
    decision: str
    action: str
    risk: str
    approved: bool
    requires_confirmation: bool
    scope: str
    boundary: str
    reason: str

    def to_dict(self) -> dict:
        return asdict(self)


class PermissionPipeline:
    """A minimal permission pipeline for harness-oriented execution decisions."""

    READ_ONLY_GIT_COMMANDS = {"status", "diff", "branch", "log", "show"}
    MUTATING_GIT_COMMANDS = {"add", "commit", "reset", "checkout", "clean", "restore"}
    HIGH_RISK_COMMANDS = {"rm", "sudo", "chmod", "chown", "dd", "mkfs", "fdisk", "shutdown", "reboot", "killall"}
    NETWORK_COMMANDS = {"curl", "wget", "nc", "netcat"}

    def __init__(self, permission_rules: PermissionRulesSpec | None = None) -> None:
        self.permission_rules = permission_rules or PermissionRulesSpec(
            name="permission_rules_builtin",
            runtime_artifact_dirs=[".claude-code", "logs"],
            standard_repo_dirs=["app", "tests", "docs", "specs", "scripts", "sample_app", "reports"],
            protected_dirs=[".git"],
        )

    def assess(self, operation: str, policy: ExecutionPolicy, *, provider_info: dict | None = None) -> PermissionDecision:
        provider_data = provider_info or {}
        provider = provider_data.get("provider", "unknown")
        provider_available = bool(provider_data.get("available", False))

        if operation == "inspect":
            return PermissionDecision(
                operation=operation,
                policy_mode=policy.mode,
                decision="allow",
                action="allow",
                risk="low",
                approved=True,
                requires_confirmation=False,
                scope="read_only",
                boundary="git_and_repo_inspection",
                reason="Read-only git inspection does not require extra approval.",
            )

        if operation == "local_loop":
            return PermissionDecision(
                operation=operation,
                policy_mode=policy.mode,
                decision="allow",
                action="allow",
                risk="medium",
                approved=True,
                requires_confirmation=False,
                scope="workspace_write",
                boundary="harness_managed_repository",
                reason="Local loop edits are allowed inside the harness-managed repository workflow.",
                recommended_flag="--show-post-review",
            )

        if operation == "delegated_provider":
            if not provider_available:
                return PermissionDecision(
                    operation=operation,
                    policy_mode=policy.mode,
                    decision="deny",
                    action="deny",
                    risk="high",
                    approved=False,
                    requires_confirmation=False,
                    scope="external_execution",
                    boundary="provider_unavailable",
                    reason=f"External provider '{provider}' is not available in the current environment.",
                )

            if policy.dangerously_skip_confirmation:
                return PermissionDecision(
                    operation=operation,
                    policy_mode=policy.mode,
                    decision="allow",
                    action="allow",
                    risk="critical",
                    approved=True,
                    requires_confirmation=False,
                    scope="external_execution",
                    boundary="external_provider_full_bypass",
                    reason=(
                        f"External provider '{provider}' is allowed to run with full bypass mode. "
                        "Use only in trusted sandboxes."
                    ),
                )

            if policy.auto_approve:
                return PermissionDecision(
                    operation=operation,
                    policy_mode=policy.mode,
                    decision="allow",
                    action="allow",
                    risk="high",
                    approved=True,
                    requires_confirmation=False,
                    scope="external_execution",
                    boundary="external_provider_auto_approved",
                    reason=f"External provider '{provider}' may run with automatic approvals enabled.",
                )

            return PermissionDecision(
                operation=operation,
                policy_mode=policy.mode,
                decision="confirm",
                action="confirm",
                risk="high",
                approved=False,
                requires_confirmation=True,
                scope="external_execution",
                boundary="external_provider_requires_explicit_approval",
                reason=(
                    f"External provider '{provider}' may execute commands outside the local loop. "
                    "Explicit approval is required."
                ),
                recommended_flag="--auto-approve",
            )

        return PermissionDecision(
            operation=operation,
            policy_mode=policy.mode,
            decision="deny",
            action="deny",
            risk="unknown",
            approved=False,
            requires_confirmation=True,
            scope="unknown",
            boundary="unknown_operation",
            reason="Unknown operation; refusing by default.",
        )

    def inspect_all(self, policy: ExecutionPolicy, *, provider_info: dict | None = None) -> dict[str, dict]:
        operations = ("inspect", "local_loop", "delegated_provider")
        return {
            operation: self.assess(operation, policy, provider_info=provider_info).to_dict()
            for operation in operations
        }

    def assess_command(self, command: list[str], policy: ExecutionPolicy, *, provider_info: dict | None = None) -> CommandPermissionDecision:
        provider_data = provider_info or {}
        provider = provider_data.get("provider", "unknown")

        if not command:
            return CommandPermissionDecision(
                command=[],
                command_text="",
                category="unknown",
                policy_mode=policy.mode,
                decision="deny",
                action="deny",
                risk="unknown",
                approved=False,
                requires_confirmation=True,
                scope="unknown",
                boundary="empty_command",
                reason="Empty command cannot be classified safely.",
            )

        binary = command[0]
        binary_name = Path(binary).name
        command_text = " ".join(command)

        if binary_name == "git" and len(command) > 1 and command[1] in self.READ_ONLY_GIT_COMMANDS:
            return CommandPermissionDecision(
                command=command,
                command_text=command_text,
                category="git_read",
                policy_mode=policy.mode,
                decision="allow",
                action="allow",
                risk="low",
                approved=True,
                requires_confirmation=False,
                scope="read_only",
                boundary="git_and_repo_inspection",
                reason="Read-only git inspection is allowed by default.",
            )

        if binary_name == "git" and len(command) > 1 and command[1] in self.MUTATING_GIT_COMMANDS:
            return CommandPermissionDecision(
                command=command,
                command_text=command_text,
                category="git_write",
                policy_mode=policy.mode,
                decision="confirm",
                action="confirm",
                risk="high",
                approved=False,
                requires_confirmation=True,
                scope="workspace_write",
                boundary="git_mutation_requires_explicit_approval",
                reason="Git-mutating commands should require explicit approval before changing repository state.",
            )

        if binary_name.startswith("python") and command[1:4] == ["-m", "unittest", "discover"]:
            return CommandPermissionDecision(
                command=command,
                command_text=command_text,
                category="test_runner",
                policy_mode=policy.mode,
                decision="allow",
                action="allow",
                risk="medium",
                approved=True,
                requires_confirmation=False,
                scope="workspace_exec",
                boundary="repository_verification",
                reason="Repository-local test execution is allowed as part of verification.",
            )

        if binary_name in {"bash", "sh"} and len(command) > 1 and command[1].startswith("scripts/"):
            return CommandPermissionDecision(
                command=command,
                command_text=command_text,
                category="repo_script",
                policy_mode=policy.mode,
                decision="allow",
                action="allow",
                risk="medium",
                approved=True,
                requires_confirmation=False,
                scope="workspace_exec",
                boundary="repository_script_execution",
                reason="Repository-local scripts are allowed, but they should stay visible inside the harness workflow.",
            )

        if binary_name in {"claude", "codex"}:
            delegated = self.assess("delegated_provider", policy, provider_info=provider_info)
            return CommandPermissionDecision(
                command=command,
                command_text=command_text,
                category="external_provider_cli",
                policy_mode=policy.mode,
                decision=delegated.decision,
                action=delegated.action,
                risk=delegated.risk,
                approved=delegated.approved,
                requires_confirmation=delegated.requires_confirmation,
                scope=delegated.scope,
                boundary=delegated.boundary,
                reason=delegated.reason,
            )

        if binary_name in self.NETWORK_COMMANDS:
            if policy.requires_confirmation():
                return CommandPermissionDecision(
                    command=command,
                    command_text=command_text,
                    category="network_access",
                    policy_mode=policy.mode,
                    decision="confirm",
                    action="confirm",
                    risk="high",
                    approved=False,
                    requires_confirmation=True,
                    scope="network_access",
                    boundary="network_access_requires_explicit_approval",
                    reason="Network-shaped commands require explicit approval before reaching external systems.",
                )
            return CommandPermissionDecision(
                command=command,
                command_text=command_text,
                category="network_access",
                policy_mode=policy.mode,
                decision="allow",
                action="allow",
                risk="high",
                approved=True,
                requires_confirmation=False,
                scope="network_access",
                boundary="network_access_auto_approved",
                reason="Network-shaped commands are allowed only because the active policy skips confirmation.",
            )

        if binary_name in self.HIGH_RISK_COMMANDS:
            return CommandPermissionDecision(
                command=command,
                command_text=command_text,
                category="high_risk_shell",
                policy_mode=policy.mode,
                decision="deny",
                action="deny",
                risk="critical",
                approved=False,
                requires_confirmation=True,
                scope="system_write",
                boundary="high_risk_shell_command",
                reason="High-risk system mutation commands should be blocked by default.",
            )

        return CommandPermissionDecision(
            command=command,
            command_text=command_text,
            category="unknown",
            policy_mode=policy.mode,
            decision="confirm",
            action="confirm",
            risk="medium",
            approved=False,
            requires_confirmation=True,
            scope="unknown",
            boundary="unclassified_command_requires_review",
            reason="Unclassified commands should be reviewed explicitly before execution.",
        )

    def inspect_command_profiles(self, policy: ExecutionPolicy, *, provider_info: dict | None = None) -> dict[str, dict]:
        provider = (provider_info or {}).get("provider", "claude_code")
        provider_binary = "codex" if provider == "codex_cli" else "claude"
        profiles = {
            "git_status": ["git", "status", "--short"],
            "unit_tests": ["python3", "-m", "unittest", "discover", "-s", "tests"],
            "verify_script": ["bash", "scripts/agent_verify.sh"],
            "git_add": ["git", "add", "README.md"],
            "delegated_provider": [provider_binary, "-p", "Reply with exactly MODEL_OK"],
            "dangerous_remove": ["rm", "-rf", "/tmp/example"],
        }
        return {
            name: self.assess_command(command, policy, provider_info=provider_info).to_dict()
            for name, command in profiles.items()
        }

    def assess_file_write(self, path: Path, repo_root: Path, policy: ExecutionPolicy | None = None) -> FileWriteDecision:
        active_policy = policy or ExecutionPolicy()
        resolved_repo_root = repo_root.resolve()
        resolved_path = path.resolve(strict=False)

        protected_dirs = {name for name in self.permission_rules.protected_dirs}
        runtime_artifact_dirs = {name for name in self.permission_rules.runtime_artifact_dirs}
        standard_repo_dirs = {name for name in self.permission_rules.standard_repo_dirs}

        protected_roots = {resolved_repo_root / name for name in protected_dirs}

        if any(resolved_path == protected_root or protected_root in resolved_path.parents for protected_root in protected_roots):
            return FileWriteDecision(
                path=str(resolved_path),
                repo_root=str(resolved_repo_root),
                policy_mode=active_policy.mode,
                decision="deny",
                action="deny",
                risk="critical",
                approved=False,
                requires_confirmation=True,
                scope="git_metadata",
                boundary="protected_repository_directory",
                reason="Writes inside protected repository directories should be blocked by default.",
            )

        if resolved_path != resolved_repo_root and resolved_repo_root not in resolved_path.parents:
            return FileWriteDecision(
                path=str(resolved_path),
                repo_root=str(resolved_repo_root),
                policy_mode=active_policy.mode,
                decision="deny",
                action="deny",
                risk="high",
                approved=False,
                requires_confirmation=True,
                scope="outside_repo",
                boundary="repository_boundary_protected",
                reason="Writes outside the target repository should be blocked by default.",
            )

        relative_parts = resolved_path.relative_to(resolved_repo_root).parts
        top_level = relative_parts[0] if relative_parts else ""

        if top_level in protected_dirs:
            return FileWriteDecision(
                path=str(resolved_path),
                repo_root=str(resolved_repo_root),
                policy_mode=active_policy.mode,
                decision="deny",
                action="deny",
                risk="critical",
                approved=False,
                requires_confirmation=True,
                scope="protected_repo_dir",
                boundary="protected_repository_directory",
                reason="Writes inside protected repository directories should be blocked by default.",
            )

        if top_level in runtime_artifact_dirs:
            return FileWriteDecision(
                path=str(resolved_path),
                repo_root=str(resolved_repo_root),
                policy_mode=active_policy.mode,
                decision="allow",
                action="allow",
                risk="low",
                approved=True,
                requires_confirmation=False,
                scope="runtime_artifact",
                boundary="runtime_artifact_directory",
                reason="Harness runtime artifacts may be written inside dedicated artifact directories.",
            )

        if top_level in standard_repo_dirs or len(relative_parts) == 1:
            return FileWriteDecision(
                path=str(resolved_path),
                repo_root=str(resolved_repo_root),
                policy_mode=active_policy.mode,
                decision="allow",
                action="allow",
                risk="medium",
                approved=True,
                requires_confirmation=False,
                scope="repo_workspace",
                boundary="repository_managed_write",
                reason="Repository-local file writes are allowed inside the harness-managed workspace.",
            )

        if active_policy.requires_confirmation():
            return FileWriteDecision(
                path=str(resolved_path),
                repo_root=str(resolved_repo_root),
                policy_mode=active_policy.mode,
                decision="confirm",
                action="confirm",
                risk="high",
                approved=False,
                requires_confirmation=True,
                scope="repo_workspace_unclassified",
                boundary="repository_unclassified_directory",
                reason="Writes to unclassified repository directories require explicit approval.",
            )

        return FileWriteDecision(
            path=str(resolved_path),
            repo_root=str(resolved_repo_root),
            policy_mode=active_policy.mode,
            decision="allow",
            action="allow",
            risk="medium",
            approved=True,
            requires_confirmation=False,
            scope="repo_workspace_unclassified",
            boundary="repository_unclassified_directory",
            reason="Unclassified repository directories are allowed only because the active policy skips confirmation.",
        )

    def inspect_write_profiles(self, repo_root: Path, policy: ExecutionPolicy | None = None) -> dict[str, dict]:
        profiles = {
            "repo_source_file": repo_root / "sample_app" / "tool_router.py",
            "repo_test_file": repo_root / "tests" / "test_tool_router.py",
            "runtime_trajectory": repo_root / ".claude-code" / "trajectories" / "run.json",
            "runtime_log_file": repo_root / "logs" / "agent.log",
            "unclassified_tmp_file": repo_root / "tmp" / "scratch.txt",
            "git_metadata": repo_root / ".git" / "config",
            "outside_repo_tmp": repo_root.parent / "outside.txt",
        }
        return {
            name: self.assess_file_write(path, repo_root, policy).to_dict()
            for name, path in profiles.items()
        }


def make_command_guard(
    pipeline: PermissionPipeline,
    policy: ExecutionPolicy,
    *,
    provider_info: dict | None = None,
) -> Callable[[list[str]], dict]:
    def guard(command: list[str]) -> dict:
        return pipeline.assess_command(command, policy, provider_info=provider_info).to_dict()

    return guard


def make_file_write_guard(
    pipeline: PermissionPipeline,
    *,
    repo_root: Path,
    policy: ExecutionPolicy | None = None,
) -> Callable[[Path], dict]:
    def guard(path: Path) -> dict:
        return pipeline.assess_file_write(path, repo_root, policy).to_dict()

    return guard
