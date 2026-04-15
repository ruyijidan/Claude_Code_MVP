from __future__ import annotations

from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.core.task_templates import build_task_artifacts
from app.runtime.ecc_adapter import ECCAdapter


class CoderAgent(BaseAgent):
    def __init__(self, spec, adapter: ECCAdapter | None = None) -> None:
        super().__init__(spec)
        self.adapter = adapter or ECCAdapter()

    def run(self, state: dict) -> dict:
        repo_path = Path(state["repo_path"])
        init_file = repo_path / "sample_app" / "__init__.py"
        task_spec = state.get("task_spec")
        task_name = task_spec.name if task_spec is not None else "implement_feature"
        artifacts = build_task_artifacts(task_name)
        module_path = repo_path / artifacts["module_path"]

        self.adapter.edit_file(
            init_file,
            '"""Sample package for starter flows."""\n',
        )
        self.adapter.edit_file(module_path, artifacts["module_content"])
        return {
            "changed_files": [str(init_file), str(module_path)],
            "implementation_status": f"written:{task_name}",
            "implementation_summary": artifacts["summary"],
        }
