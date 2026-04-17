from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class TaskSpec:
    name: str
    goal: str
    inputs: dict[str, str]
    outputs: dict[str, str]
    constraints: list[str]
    tools: list[str]
    done_when: list[str]


@dataclass(slots=True)
class AgentSpec:
    name: str
    role: str
    system_prompt: str
    allowed_tools: list[str]
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    constraints: list[str] = field(default_factory=list)


@dataclass(slots=True)
class WorkflowSpec:
    name: str
    goal: str
    entry_signals: list[str]
    required_context: list[str]
    steps: list[str]
    verification: list[str]
    stop_conditions: list[str]


@dataclass(slots=True)
class RuleSpec:
    name: str
    intent: str
    applies_to: list[str]
    checks: list[str]
    failure_message: str


@dataclass(slots=True)
class PermissionRulesSpec:
    name: str
    runtime_artifact_dirs: list[str]
    standard_repo_dirs: list[str]
    protected_dirs: list[str]


@dataclass(slots=True)
class PlanStep:
    id: str
    description: str
    agent: str
    status: str = "pending"


@dataclass(slots=True)
class TrajectoryEvent:
    stage: str
    status: str
    detail: str


@dataclass(slots=True)
class RunContext:
    repo_path: Path
    task_name: str
