from __future__ import annotations

from app.agent.loop import CodingAgentLoop
from app.agent.policies import ExecutionPolicy, PermissionPipeline, make_command_guard
from app.core.memory_store import MemoryStore
from app.core.spec_loader import SpecLoader
from app.runtime.adapter_factory import build_runtime_adapter


class GraphExecutor:
    def __init__(self, spec_loader: SpecLoader, memory_store: MemoryStore, runtime_provider: str | None = None) -> None:
        self.spec_loader = spec_loader
        self.memory_store = memory_store
        self.adapter = build_runtime_adapter(runtime_provider)
        policy = ExecutionPolicy()
        permission_pipeline = PermissionPipeline()
        self.adapter.configure_command_guard(
            make_command_guard(permission_pipeline, policy, provider_info=self.adapter.provider_info())
        )
        self.loop = CodingAgentLoop(spec_loader=spec_loader, memory_store=memory_store, adapter=self.adapter)

    def execute(self, initial_state: dict) -> dict:
        state = dict(initial_state)
        prompt = state["request"]["feature_request"]
        task_spec = state.get("task_spec")
        task_name = task_spec.name if task_spec is not None else None
        return self.loop.run(repo_path=state["repo_path"], prompt=prompt, task_name=task_name)
