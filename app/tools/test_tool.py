from __future__ import annotations

from pathlib import Path

from app.runtime.ecc_adapter import ECCAdapter
from app.tools.base_tool import BaseTool


class TestTool(BaseTool):
    name = "test_tool"

    def __init__(self, adapter: ECCAdapter | None = None) -> None:
        self.adapter = adapter or ECCAdapter()

    def invoke(self, repo_path: str) -> dict:
        code, output = self.adapter.run_tests(Path(repo_path))
        return {"returncode": code, "output": output}
