from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.runtime.api_adapter import AnthropicCompatibleAdapter, GLM5Adapter
from app.runtime.cli_adapter import ClaudeCodeAdapter, CodexCLIAdapter


class ProviderDelegationTests(unittest.TestCase):
    def test_claude_adapter_builds_noninteractive_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            adapter = ClaudeCodeAdapter()
            adapter.run_command = lambda cmd, cwd: (0, "ok")  # type: ignore[method-assign]
            code, output, command = adapter.execute_prompt("fix failing tests", Path(tmp_dir), auto_approve=False)
            self.assertIsInstance(code, int)
            self.assertIsInstance(output, str)
            self.assertEqual(command[:4], ["claude", "-p", "--output-format", "json"])

    def test_codex_adapter_builds_exec_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            adapter = CodexCLIAdapter()
            adapter.run_command = lambda cmd, cwd: (0, "ok")  # type: ignore[method-assign]
            code, output, command = adapter.execute_prompt("fix failing tests", Path(tmp_dir), auto_approve=False)
            self.assertIsInstance(code, int)
            self.assertIsInstance(output, str)
            self.assertEqual(command[:2], ["codex", "--cd"])
            self.assertIn("--skip-git-repo-check", command)
            self.assertIn("--full-auto", command)

    def test_anthropic_compatible_adapter_uses_messages_api(self) -> None:
        adapter = AnthropicCompatibleAdapter()
        payload = {
            "content": [{"type": "text", "text": "MODEL_OK"}],
        }

        class _Response:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self) -> bytes:
                import json

                return json.dumps(payload).encode("utf-8")

        with patch.dict(
            "os.environ",
            {
                "ANTHROPIC_BASE_URL": "https://example.test",
                "ANTHROPIC_AUTH_TOKEN": "secret",
                "ANTHROPIC_MODEL": "glm-5",
            },
            clear=False,
        ):
            with patch("urllib.request.urlopen", return_value=_Response()) as mocked_urlopen:
                code, output, command = adapter.execute_prompt("fix failing tests", Path("."))

        self.assertEqual(code, 0)
        self.assertEqual(command, ["POST", "https://example.test/v1/messages"])
        self.assertIn('"result": "MODEL_OK"', output)
        request = mocked_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://example.test/v1/messages")

    def test_glm5_adapter_reports_glm5_provider_name(self) -> None:
        adapter = GLM5Adapter()
        with patch.dict(
            "os.environ",
            {
                "ANTHROPIC_BASE_URL": "https://example.test",
                "ANTHROPIC_AUTH_TOKEN": "secret",
                "ANTHROPIC_MODEL": "glm-5",
            },
            clear=False,
        ):
            with patch.object(adapter, "_should_bypass_proxy", return_value=True):
                with patch.object(adapter, "can_delegate_prompt", return_value=True):
                    info = adapter.provider_info()
        self.assertEqual(info["provider"], "glm5")
        self.assertTrue(info["bypass_proxy"])

    def test_anthropic_adapter_bypasses_proxy_for_private_hosts(self) -> None:
        adapter = AnthropicCompatibleAdapter()
        with patch("socket.getaddrinfo", return_value=[(None, None, None, None, ("10.1.72.56", 443))]):
            self.assertTrue(adapter._should_bypass_proxy("https://llm-api.zego.cloud", ""))

    def test_anthropic_adapter_can_explicitly_bypass_proxy(self) -> None:
        adapter = AnthropicCompatibleAdapter()
        self.assertTrue(adapter._should_bypass_proxy("https://example.test", "1"))

    def test_anthropic_adapter_uses_proxyless_opener_when_bypass_is_enabled(self) -> None:
        adapter = AnthropicCompatibleAdapter()
        request = MagicMock()
        opener = MagicMock()
        with patch("urllib.request.build_opener", return_value=opener) as mocked_build_opener:
            adapter._open_request(request, bypass_proxy=True)
        mocked_build_opener.assert_called_once()
        opener.open.assert_called_once()


if __name__ == "__main__":
    unittest.main()
