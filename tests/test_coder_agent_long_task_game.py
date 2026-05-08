from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.agents.coder_agent import CoderAgent
from app.core.models import AgentSpec, TaskSpec
from app.runtime.ecc_adapter import ECCAdapter


class CoderAgentLongTaskGameTests(unittest.TestCase):
    def test_long_task_game_writes_halo_drift_artifact(self) -> None:
        spec = AgentSpec(
            name="coder",
            role="coder",
            system_prompt="",
            allowed_tools=[],
            input_schema={},
            output_schema={},
        )
        task_spec = TaskSpec(
            name="long_task_game",
            goal="Improve a browser mini-game",
            inputs={},
            outputs={},
            constraints=[],
            tools=[],
            done_when=[],
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            agent = CoderAgent(spec, ECCAdapter())
            result = agent.run({"repo_path": repo_path, "task_spec": task_spec})
            game_file = repo_path / "examples" / "halo-drift" / "game.js"
            self.assertTrue(game_file.exists())
            self.assertTrue(any(path.endswith("examples/halo-drift/game.js") for path in result["changed_files"]))


if __name__ == "__main__":
    unittest.main()
