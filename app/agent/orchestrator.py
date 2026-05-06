from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.core.models import AgentSpec


SHARED_RUNTIME_KEYS = {
    "repo_path",
    "request",
    "task_spec",
    "workflow_spec",
    "provider_info",
    "runtime_provider",
    "repo_context",
    "plan",
    "workflow_execution",
    "changed_files",
    "implementation_summary",
    "test_result",
    "verification_errors",
    "gate_failures",
    "application_verification",
    "critic_issues",
}


@dataclass(slots=True)
class AgentTransition:
    agent: str
    role: str
    status: str
    allowed_tools: list[str]
    declared_input_keys: list[str]
    declared_output_keys: list[str]
    observed_input_keys: list[str]
    observed_output_keys: list[str]
    next_agent: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AgentOrchestrator:
    def __init__(self) -> None:
        self.transitions: list[AgentTransition] = []

    def isolated_state(self, spec: AgentSpec, state: dict[str, Any]) -> dict[str, Any]:
        allowed_keys = set(spec.input_schema) | SHARED_RUNTIME_KEYS
        isolated: dict[str, Any] = {}
        for key in allowed_keys:
            if key in state:
                isolated[key] = state[key]
        return isolated

    def record_transition(
        self,
        spec: AgentSpec,
        state_before: dict[str, Any],
        result: dict[str, Any],
        *,
        status: str,
        next_agent: str | None = None,
    ) -> None:
        transition = AgentTransition(
            agent=spec.name,
            role=spec.role,
            status=status,
            allowed_tools=list(spec.allowed_tools),
            declared_input_keys=sorted(spec.input_schema.keys()),
            declared_output_keys=sorted(spec.output_schema.keys()),
            observed_input_keys=sorted(key for key in state_before if key in self.isolated_state(spec, state_before)),
            observed_output_keys=sorted(result.keys()),
            next_agent=next_agent,
        )
        self.transitions.append(transition)

    def history(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self.transitions]
