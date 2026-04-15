from __future__ import annotations

from datetime import datetime, timezone

from app.core.memory_store import MemoryStore


class ReplayLogger:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def persist(self, state: dict) -> str:
        name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        payload = {
            "task": state["task_spec"].name,
            "runtime_provider": state.get("runtime_provider"),
            "provider_info": state.get("provider_info", {}),
            "plan": state.get("plan", []),
            "changed_files": state.get("changed_files", []),
            "test_result": state.get("test_result"),
            "verification_errors": state.get("verification_errors", []),
            "completion_check": state.get("completion_check", {}),
            "gate_results": state.get("gate_results", []),
            "failure_signals": state.get("failure_signals", []),
            "repair_decision": state.get("repair_decision", {}),
            "repair_attempts": state.get("repair_attempts", []),
            "score": state.get("score"),
        }
        return str(self.store.write(name, payload))
