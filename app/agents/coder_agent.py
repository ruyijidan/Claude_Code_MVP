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
        task_spec = state.get("task_spec")
        task_name = task_spec.name if task_spec is not None else "implement_feature"
        artifacts = build_task_artifacts(task_name)
        module_path = repo_path / artifacts["module_path"]
        changed_files: list[str] = []

        if task_name != "long_task_game":
            init_file = repo_path / "app" / "__init__.py"
            self.adapter.edit_file(
                init_file,
                '"""Generated application package for starter flows."""\n',
            )
            changed_files.append(str(init_file))

        self.adapter.edit_file(module_path, artifacts["module_content"])
        changed_files.append(str(module_path))

        test_path = artifacts.get("test_path")
        test_content = artifacts.get("test_content")
        if task_name == "long_task_game" and isinstance(test_path, str) and isinstance(test_content, str):
            self.adapter.edit_file(repo_path / test_path, test_content)
            changed_files.append(str(repo_path / test_path))

        return {
            "changed_files": changed_files,
            "implementation_status": f"written:{task_name}",
            "implementation_summary": artifacts["summary"],
        }
