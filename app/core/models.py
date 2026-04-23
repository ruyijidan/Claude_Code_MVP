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
    clarification_fields: list[str] = field(default_factory=list)


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


@dataclass(slots=True)
class ClarificationQuestion:
    key: str
    question: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {
            "key": self.key,
            "question": self.question,
            "reason": self.reason,
        }


@dataclass(slots=True)
class ContinuationCandidate:
    label: str
    task_type: str | None = None
    request_prompt: str | None = None
    summary: str | None = None
    timestamp: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "task_type": self.task_type,
            "request_prompt": self.request_prompt,
            "summary": self.summary,
            "timestamp": self.timestamp,
        }


@dataclass(slots=True)
class IntentClarificationResult:
    status: str
    normalized_prompt: str
    inferred_task_type: str | None = None
    continuation_target: str | None = None
    kickoff_message: str | None = None
    continuation_candidates: list[ContinuationCandidate] = field(default_factory=list)
    missing_constraints: list[str] = field(default_factory=list)
    questions: list[ClarificationQuestion] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "normalized_prompt": self.normalized_prompt,
            "inferred_task_type": self.inferred_task_type,
            "continuation_target": self.continuation_target,
            "kickoff_message": self.kickoff_message,
            "continuation_candidates": [candidate.to_dict() for candidate in self.continuation_candidates],
            "missing_constraints": list(self.missing_constraints),
            "questions": [question.to_dict() for question in self.questions],
        }
