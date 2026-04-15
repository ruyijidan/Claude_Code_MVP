from __future__ import annotations

import json
from pathlib import Path

from app.agent.loop import CodingAgentLoop
from app.core.env_loader import load_project_env
from app.core.memory_store import MemoryStore
from app.core.spec_loader import SpecLoader
from app.runtime.adapter_factory import build_runtime_adapter


def run_task(repo_path: Path, task_name: str, request_text: str, runtime_provider: str | None = None) -> dict:
    load_project_env(repo_path)
    spec_root = Path(__file__).resolve().parents[1] / "specs"
    loader = SpecLoader(spec_root)
    adapter = build_runtime_adapter(runtime_provider)
    loop = CodingAgentLoop(
        spec_loader=loader,
        memory_store=MemoryStore(repo_path / ".claude-code" / "trajectories"),
        adapter=adapter,
    )
    return loop.run(repo_path=repo_path, prompt=request_text, task_name=task_name)


if __name__ == "__main__":
    workspace = Path("workspace")
    workspace.mkdir(exist_ok=True)
    result = run_task(workspace, "implement_feature", "Add a tool router and tests")
    print(json.dumps(result, indent=2, default=str))
