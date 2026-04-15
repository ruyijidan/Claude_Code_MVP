from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.agents.coder_agent import CoderAgent
from app.core.models import AgentSpec
from app.runtime.ecc_adapter import ECCAdapter


class ToolRouterCodegenTests(unittest.TestCase):
    def test_coder_writes_tool_router_module(self) -> None:
        spec = AgentSpec(
            name="coder",
            role="coder",
            system_prompt="",
            allowed_tools=[],
            input_schema={},
            output_schema={},
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            agent = CoderAgent(spec, ECCAdapter())
            result = agent.run({"repo_path": repo_path})
            router_file = repo_path / "sample_app" / "tool_router.py"
            self.assertTrue(router_file.exists())
            self.assertEqual(len(result["changed_files"]), 2)


if __name__ == "__main__":
    unittest.main()
