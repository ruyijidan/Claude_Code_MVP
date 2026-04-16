from __future__ import annotations

import json
from pathlib import Path

from app.agent.loop import CodingAgentLoop
from app.core.env_loader import load_project_env, resolve_auth_loading_policy
from app.core.memory_store import MemoryStore
from app.core.spec_loader import SpecLoader
from app.runtime.adapter_factory import build_runtime_adapter


def run_task(
    repo_path: Path,
    task_name: str,
    request_text: str,
    runtime_provider: str | None = None,
    auth_source: str = "auto",
) -> dict:
    selected_provider, excluded_prefixes = resolve_auth_loading_policy(repo_path, runtime_provider, auth_source)
    load_project_env(repo_path, exclude_prefixes=excluded_prefixes)
    spec_root = Path(__file__).resolve().parents[1] / "specs"
    loader = SpecLoader(spec_root)
    adapter = build_runtime_adapter(selected_provider)
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
