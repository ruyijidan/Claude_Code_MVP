from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.core.memory_store import MemoryStore
from app.core.spec_loader import SpecLoader
from app.graph.executor import GraphExecutor


class DaemonService:
    def __init__(self, spec_root: Path, trajectory_root_name: str = ".claude-code/trajectories") -> None:
        self.spec_root = spec_root
        self.trajectory_root_name = trajectory_root_name

    def run_task(
        self,
        *,
        repo_path: str,
        request_prompt: str,
        task_name: str | None = None,
        runtime_provider: str | None = None,
    ) -> dict[str, Any]:
        repo = Path(repo_path).resolve()
        loader = SpecLoader(self.spec_root)
        memory_store = MemoryStore(repo / self.trajectory_root_name)
        executor = GraphExecutor(loader, memory_store, runtime_provider=runtime_provider)
        state = {
            "repo_path": repo,
            "request": {
                "repo_path": str(repo),
                "feature_request": request_prompt,
            },
        }
        if task_name is not None:
            state["task_spec"] = loader.load_task(task_name)
        result = executor.execute(state)
        return self._result_summary(result)

    def latest_run(self, *, repo_path: str) -> dict[str, Any] | None:
        repo = Path(repo_path).resolve()
        memory_store = MemoryStore(repo / self.trajectory_root_name)
        payload = memory_store.read_latest()
        if payload is None:
            return None
        return payload

    def run_status(self, *, repo_path: str) -> dict[str, Any]:
        latest = self.latest_run(repo_path=repo_path)
        if latest is None:
            return {
                "available": False,
                "status": "missing",
            }
        return {
            "available": True,
            "status": latest.get("test_result"),
            "task": latest.get("task"),
            "workflow": latest.get("workflow"),
            "selected_path": latest.get("workflow_execution", {}).get("selected_path"),
            "agent_transition_count": len(latest.get("agent_transitions", [])),
            "trajectory_path": latest.get("trajectory_path"),
        }

    def _result_summary(self, result: dict[str, Any]) -> dict[str, Any]:
        return {
            "task": result["task_spec"].name,
            "runtime_provider": result.get("runtime_provider"),
            "status": result.get("test_result"),
            "selected_path": result.get("selected_path"),
            "workflow": result.get("workflow_spec").name if result.get("workflow_spec") is not None else None,
            "workflow_status": result.get("workflow_execution", {}).get("status"),
            "agent_transition_count": len(result.get("agent_transitions", [])),
            "changed_files": list(result.get("changed_files", [])),
            "trajectory_path": result.get("trajectory_path"),
        }

    def to_json(self, payload: dict[str, Any]) -> bytes:
        return json.dumps(payload, indent=2, default=str).encode("utf-8")
