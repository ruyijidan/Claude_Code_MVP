from __future__ import annotations

from dataclasses import asdict, dataclass


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
    risk: str
    approved: bool
    requires_confirmation: bool
    reason: str
    recommended_flag: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class PermissionPipeline:
    """A minimal permission pipeline for harness-oriented execution decisions."""

    def assess(self, operation: str, policy: ExecutionPolicy, *, provider_info: dict | None = None) -> PermissionDecision:
        provider = (provider_info or {}).get("provider")

        if operation == "inspect":
            return PermissionDecision(
                operation=operation,
                policy_mode=policy.mode,
                risk="low",
                approved=True,
                requires_confirmation=False,
                reason="Read-only git inspection does not require extra approval.",
            )

        if operation == "local_loop":
            return PermissionDecision(
                operation=operation,
                policy_mode=policy.mode,
                risk="medium",
                approved=True,
                requires_confirmation=policy.requires_confirmation(),
                reason="Local loop edits are allowed inside the harness-managed repository workflow.",
                recommended_flag="--show-post-review",
            )

        if operation == "delegated_provider":
            if policy.dangerously_skip_confirmation:
                return PermissionDecision(
                    operation=operation,
                    policy_mode=policy.mode,
                    risk="critical",
                    approved=True,
                    requires_confirmation=False,
                    reason=(
                        f"External provider '{provider}' is allowed to run with full bypass mode. "
                        "Use only in trusted sandboxes."
                    ),
                )

            if policy.auto_approve:
                return PermissionDecision(
                    operation=operation,
                    policy_mode=policy.mode,
                    risk="high",
                    approved=True,
                    requires_confirmation=False,
                    reason=f"External provider '{provider}' may run with automatic approvals enabled.",
                )

            return PermissionDecision(
                operation=operation,
                policy_mode=policy.mode,
                risk="high",
                approved=False,
                requires_confirmation=True,
                reason=(
                    f"External provider '{provider}' may execute commands outside the local loop. "
                    "Explicit approval is required."
                ),
                recommended_flag="--auto-approve",
            )

        return PermissionDecision(
            operation=operation,
            policy_mode=policy.mode,
            risk="unknown",
            approved=False,
            requires_confirmation=True,
            reason="Unknown operation; refusing by default.",
        )
