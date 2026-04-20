from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from app.runtime.adapter_factory import build_runtime_adapter


LIVE_FLAG = "CC_RUN_LIVE_PROVIDER_TESTS"
API_PROVIDER_ENV = "CC_LIVE_API_PROVIDER"
CLI_PROVIDER_ENV = "CC_LIVE_CLI_PROVIDER"
LIVE_PROMPT = "Reply with exactly MODEL_OK"


def _live_tests_enabled() -> bool:
    return os.getenv(LIVE_FLAG, "").strip().lower() in {"1", "true", "yes", "on"}


@unittest.skipUnless(_live_tests_enabled(), f"set {LIVE_FLAG}=1 to run live provider acceptance tests")
class LiveProviderIntegrationTests(unittest.TestCase):
    def test_live_api_provider_minimal_roundtrip(self) -> None:
        provider_name = os.getenv(API_PROVIDER_ENV, "").strip()
        if not provider_name:
            self.skipTest(f"set {API_PROVIDER_ENV} to a live API provider such as glm5 or anthropic_api")
        if provider_name not in {"glm5", "anthropic_api"}:
            self.skipTest(f"unsupported live API provider: {provider_name}")

        adapter = build_runtime_adapter(provider_name)
        info = adapter.provider_info()
        if not info.get("available"):
            self.skipTest(f"provider {provider_name} is not configured for live execution")

        with tempfile.TemporaryDirectory() as tmp_dir:
            code, output, command = adapter.execute_prompt(LIVE_PROMPT, Path(tmp_dir))

        self.assertEqual(code, 0, msg=f"live API call failed: {output}")
        self.assertTrue(command, msg="expected a live API command descriptor")
        payload = json.loads(output)
        self.assertEqual(payload.get("provider"), provider_name)
        self.assertIn("MODEL_OK", payload.get("result", ""))

    def test_live_cli_provider_minimal_roundtrip(self) -> None:
        provider_name = os.getenv(CLI_PROVIDER_ENV, "").strip()
        if not provider_name:
            self.skipTest(f"set {CLI_PROVIDER_ENV} to claude_code or codex_cli")
        if provider_name not in {"claude_code", "codex_cli"}:
            self.skipTest(f"unsupported live CLI provider: {provider_name}")

        adapter = build_runtime_adapter(provider_name)
        info = adapter.provider_info()
        binary_name = info.get("binary")
        if binary_name and shutil.which(binary_name) is None:
            self.skipTest(f"required CLI binary {binary_name!r} is not installed")
        if not info.get("available"):
            self.skipTest(f"provider {provider_name} is not available for live execution")

        with tempfile.TemporaryDirectory() as tmp_dir:
            code, output, command = adapter.execute_prompt(LIVE_PROMPT, Path(tmp_dir), auto_approve=True)

        self.assertEqual(code, 0, msg=f"live CLI call failed: {output}")
        self.assertTrue(command, msg="expected a delegated CLI command")
        self.assertIn("MODEL_OK", output)


if __name__ == "__main__":
    unittest.main()
