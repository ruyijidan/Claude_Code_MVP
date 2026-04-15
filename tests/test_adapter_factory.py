from __future__ import annotations

import unittest

from app.runtime.adapter_factory import build_runtime_adapter


class AdapterFactoryTests(unittest.TestCase):
    def test_builds_supported_providers(self) -> None:
        self.assertEqual(build_runtime_adapter().provider_name, "local")
        self.assertEqual(build_runtime_adapter("claude_code").provider_name, "claude_code")
        self.assertEqual(build_runtime_adapter("codex_cli").provider_name, "codex_cli")


if __name__ == "__main__":
    unittest.main()
