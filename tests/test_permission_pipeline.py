from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.agent.policies import ExecutionPolicy, PermissionPipeline
from app.core.spec_loader import SpecLoader


class PermissionPipelineTests(unittest.TestCase):
    def test_permission_pipeline_can_read_directory_tiers_from_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            spec_root = Path(tmp_dir) / "specs"
            rules_dir = spec_root / "rules"
            rules_dir.mkdir(parents=True)
            (rules_dir / "permission-rules.yaml").write_text(
                json.dumps(
                    {
                        "name": "custom_rules",
                        "runtime_artifact_dirs": ["artifacts"],
                        "standard_repo_dirs": ["src"],
                        "protected_dirs": [".meta"],
                    }
                ),
                encoding="utf-8",
            )
            rules = SpecLoader(spec_root).load_permission_rules()
            pipeline = PermissionPipeline(rules)

            repo_root = Path(tmp_dir) / "repo"
            repo_root.mkdir()
            src_decision = pipeline.assess_file_write(repo_root / "src" / "main.py", repo_root)
            artifact_decision = pipeline.assess_file_write(repo_root / "artifacts" / "run.json", repo_root)
            protected_decision = pipeline.assess_file_write(repo_root / ".meta" / "state.json", repo_root)

        self.assertEqual(src_decision.boundary, "repository_managed_write")
        self.assertEqual(artifact_decision.boundary, "runtime_artifact_directory")
        self.assertEqual(protected_decision.boundary, "protected_repository_directory")

    def test_inspect_is_always_allowed(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess("inspect", ExecutionPolicy())
        self.assertTrue(decision.approved)
        self.assertEqual(decision.action, "allow")
        self.assertEqual(decision.decision, "allow")
        self.assertEqual(decision.risk, "low")
        self.assertEqual(decision.scope, "read_only")

    def test_local_loop_is_allowed_but_marked_medium_risk(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess("local_loop", ExecutionPolicy())
        self.assertTrue(decision.approved)
        self.assertEqual(decision.action, "allow")
        self.assertEqual(decision.decision, "allow")
        self.assertEqual(decision.risk, "medium")
        self.assertEqual(decision.boundary, "harness_managed_repository")
        self.assertFalse(decision.requires_confirmation)

    def test_delegated_provider_requires_explicit_approval_by_default(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess(
            "delegated_provider",
            ExecutionPolicy(),
            provider_info={"provider": "codex_cli", "available": True},
        )
        self.assertFalse(decision.approved)
        self.assertTrue(decision.requires_confirmation)
        self.assertEqual(decision.action, "confirm")
        self.assertEqual(decision.decision, "confirm")
        self.assertEqual(decision.recommended_flag, "--auto-approve")

    def test_delegated_provider_is_allowed_in_auto_mode(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess(
            "delegated_provider",
            ExecutionPolicy(auto_approve=True),
            provider_info={"provider": "codex_cli", "available": True},
        )
        self.assertTrue(decision.approved)
        self.assertEqual(decision.action, "allow")
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
        self.assertEqual(decision.action, "confirm")
        self.assertEqual(decision.decision, "confirm")

    def test_high_risk_shell_command_is_denied(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess_command(["rm", "-rf", "/tmp/example"], ExecutionPolicy())
        self.assertEqual(decision.category, "high_risk_shell")
        self.assertFalse(decision.approved)
        self.assertEqual(decision.action, "deny")
        self.assertEqual(decision.risk, "critical")

    def test_network_command_requires_confirmation_by_default(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess_command(["curl", "https://example.com"], ExecutionPolicy())
        self.assertEqual(decision.category, "network_access")
        self.assertEqual(decision.action, "confirm")
        self.assertFalse(decision.approved)
        self.assertTrue(decision.requires_confirmation)

    def test_network_command_is_allowed_in_auto_mode(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess_command(["curl", "https://example.com"], ExecutionPolicy(auto_approve=True))
        self.assertEqual(decision.category, "network_access")
        self.assertEqual(decision.action, "allow")
        self.assertTrue(decision.approved)

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
        self.assertEqual(snapshot["git_add"]["action"], "confirm")

    def test_repo_local_file_write_is_allowed(self) -> None:
        pipeline = PermissionPipeline()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            decision = pipeline.assess_file_write(repo_root / "sample_app" / "tool_router.py", repo_root)
        self.assertTrue(decision.approved)
        self.assertEqual(decision.boundary, "repository_managed_write")
        self.assertFalse(decision.requires_confirmation)

    def test_runtime_artifact_write_is_allowed_with_artifact_scope(self) -> None:
        pipeline = PermissionPipeline()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            decision = pipeline.assess_file_write(repo_root / ".claude-code" / "trajectories" / "run.json", repo_root)
        self.assertTrue(decision.approved)
        self.assertEqual(decision.scope, "runtime_artifact")
        self.assertEqual(decision.boundary, "runtime_artifact_directory")
        self.assertEqual(decision.risk, "low")

    def test_unclassified_repo_directory_requires_confirmation_by_default(self) -> None:
        pipeline = PermissionPipeline()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            decision = pipeline.assess_file_write(repo_root / "tmp" / "scratch.txt", repo_root)
        self.assertFalse(decision.approved)
        self.assertTrue(decision.requires_confirmation)
        self.assertEqual(decision.action, "confirm")
        self.assertEqual(decision.decision, "confirm")
        self.assertEqual(decision.scope, "repo_workspace_unclassified")
        self.assertEqual(decision.boundary, "repository_unclassified_directory")

    def test_unclassified_repo_directory_is_allowed_in_auto_mode(self) -> None:
        pipeline = PermissionPipeline()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            decision = pipeline.assess_file_write(
                repo_root / "tmp" / "scratch.txt",
                repo_root,
                ExecutionPolicy(auto_approve=True),
            )
        self.assertTrue(decision.approved)
        self.assertFalse(decision.requires_confirmation)
        self.assertEqual(decision.decision, "allow")

    def test_git_metadata_write_is_denied(self) -> None:
        pipeline = PermissionPipeline()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            decision = pipeline.assess_file_write(repo_root / ".git" / "config", repo_root)
        self.assertFalse(decision.approved)
        self.assertEqual(decision.boundary, "protected_repository_directory")

    def test_outside_repo_write_is_denied(self) -> None:
        pipeline = PermissionPipeline()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            outside = repo_root.parent / "outside.txt"
            decision = pipeline.assess_file_write(outside, repo_root)
        self.assertFalse(decision.approved)
        self.assertEqual(decision.boundary, "repository_boundary_protected")


if __name__ == "__main__":
    unittest.main()
