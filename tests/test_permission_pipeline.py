from __future__ import annotations

import unittest

from app.agent.policies import ExecutionPolicy, PermissionPipeline


class PermissionPipelineTests(unittest.TestCase):
    def test_inspect_is_always_allowed(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess("inspect", ExecutionPolicy())
        self.assertTrue(decision.approved)
        self.assertEqual(decision.decision, "allow")
        self.assertEqual(decision.risk, "low")
        self.assertEqual(decision.scope, "read_only")

    def test_local_loop_is_allowed_but_marked_medium_risk(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess("local_loop", ExecutionPolicy())
        self.assertTrue(decision.approved)
        self.assertEqual(decision.decision, "allow_with_confirmation")
        self.assertEqual(decision.risk, "medium")
        self.assertEqual(decision.boundary, "harness_managed_repository")

    def test_delegated_provider_requires_explicit_approval_by_default(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess(
            "delegated_provider",
            ExecutionPolicy(),
            provider_info={"provider": "codex_cli", "available": True},
        )
        self.assertFalse(decision.approved)
        self.assertTrue(decision.requires_confirmation)
        self.assertEqual(decision.decision, "require_confirmation")
        self.assertEqual(decision.recommended_flag, "--auto-approve")

    def test_delegated_provider_is_allowed_in_auto_mode(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess(
            "delegated_provider",
            ExecutionPolicy(auto_approve=True),
            provider_info={"provider": "codex_cli", "available": True},
        )
        self.assertTrue(decision.approved)
        self.assertEqual(decision.decision, "allow")
        self.assertEqual(decision.risk, "high")

    def test_delegated_provider_is_denied_when_provider_is_unavailable(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess(
            "delegated_provider",
            ExecutionPolicy(auto_approve=True),
            provider_info={"provider": "codex_cli", "available": False},
        )
        self.assertFalse(decision.approved)
        self.assertEqual(decision.decision, "deny")
        self.assertEqual(decision.boundary, "provider_unavailable")

    def test_permission_snapshot_contains_all_operations(self) -> None:
        pipeline = PermissionPipeline()
        snapshot = pipeline.inspect_all(
            ExecutionPolicy(),
            provider_info={"provider": "local", "available": True},
        )
        self.assertEqual(set(snapshot.keys()), {"inspect", "local_loop", "delegated_provider"})
        self.assertEqual(snapshot["inspect"]["decision"], "allow")

    def test_read_only_git_command_is_low_risk(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess_command(["git", "status", "--short"], ExecutionPolicy())
        self.assertEqual(decision.category, "git_read")
        self.assertTrue(decision.approved)
        self.assertEqual(decision.risk, "low")

    def test_git_mutation_requires_confirmation(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess_command(["git", "add", "README.md"], ExecutionPolicy())
        self.assertEqual(decision.category, "git_write")
        self.assertFalse(decision.approved)
        self.assertEqual(decision.decision, "require_confirmation")

    def test_high_risk_shell_command_is_denied(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess_command(["rm", "-rf", "/tmp/example"], ExecutionPolicy())
        self.assertEqual(decision.category, "high_risk_shell")
        self.assertFalse(decision.approved)
        self.assertEqual(decision.risk, "critical")

    def test_command_profiles_include_representative_commands(self) -> None:
        pipeline = PermissionPipeline()
        snapshot = pipeline.inspect_command_profiles(
            ExecutionPolicy(),
            provider_info={"provider": "codex_cli", "available": True},
        )
        self.assertIn("git_status", snapshot)
        self.assertIn("delegated_provider", snapshot)
        self.assertEqual(snapshot["git_status"]["category"], "git_read")
        self.assertEqual(snapshot["dangerous_remove"]["decision"], "deny")


if __name__ == "__main__":
    unittest.main()
