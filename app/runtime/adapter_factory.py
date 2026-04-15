from __future__ import annotations

import os

from app.runtime.cli_adapter import ClaudeCodeAdapter, CodexCLIAdapter
from app.runtime.local_runtime import LocalRuntimeAdapter


def build_runtime_adapter(provider: str | None = None) -> LocalRuntimeAdapter:
    selected = (provider or os.getenv("SPEC_RUNTIME_PROVIDER", "local")).lower()
    if selected == "mock":
        return LocalRuntimeAdapter()
    if selected == "local":
        return LocalRuntimeAdapter()
    if selected == "claude_code":
        return ClaudeCodeAdapter()
    if selected == "codex_cli":
        return CodexCLIAdapter()
    return LocalRuntimeAdapter()
