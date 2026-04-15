from __future__ import annotations

import unittest

from app.agent.policies import ExecutionPolicy, PermissionPipeline


class PermissionPipelineTests(unittest.TestCase):
    def test_inspect_is_always_allowed(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess("inspect", ExecutionPolicy())
        self.assertTrue(decision.approved)
        self.assertEqual(decision.risk, "low")

    def test_local_loop_is_allowed_but_marked_medium_risk(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess("local_loop", ExecutionPolicy())
        self.assertTrue(decision.approved)
        self.assertEqual(decision.risk, "medium")

    def test_delegated_provider_requires_explicit_approval_by_default(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess("delegated_provider", ExecutionPolicy(), provider_info={"provider": "codex_cli"})
        self.assertFalse(decision.approved)
        self.assertTrue(decision.requires_confirmation)
        self.assertEqual(decision.recommended_flag, "--auto-approve")

    def test_delegated_provider_is_allowed_in_auto_mode(self) -> None:
        pipeline = PermissionPipeline()
        decision = pipeline.assess(
            "delegated_provider",
            ExecutionPolicy(auto_approve=True),
            provider_info={"provider": "codex_cli"},
        )
        self.assertTrue(decision.approved)
        self.assertEqual(decision.risk, "high")


if __name__ == "__main__":
    unittest.main()
