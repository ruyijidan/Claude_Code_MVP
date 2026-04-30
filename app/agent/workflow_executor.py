from __future__ import annotations

from app.core.models import TaskSpec, WorkflowSpec
from app.core.tool_registry import ToolRegistry
from app.runtime.artifact_readers import ArtifactReaderRegistry


class WorkflowExecutor:
    def __init__(self, tool_registry: ToolRegistry, reader_registry: ArtifactReaderRegistry) -> None:
        self.tool_registry = tool_registry
        self.reader_registry = reader_registry

    def begin(self, task_spec: TaskSpec, workflow: WorkflowSpec, context: dict, plan: list[dict]) -> dict:
        reader_names = self._active_reader_names(context.get("application_legibility", {}).get("reader_results", []))
        return {
            "workflow": workflow.name,
            "goal": workflow.goal,
            "status": "running",
            "required_context": list(workflow.required_context),
            "verification_targets": list(workflow.verification),
            "stop_conditions": list(workflow.stop_conditions),
            "selected_tools": self.tool_registry.describe_many(task_spec.tools),
            "selected_readers": self.reader_registry.describe_many(reader_names),
            "plan_step_ids": [step.get("id") for step in plan],
            "steps": [
                {
                    "id": f"workflow_step_{index}",
                    "description": step,
                    "status": "pending",
                }
                for index, step in enumerate(workflow.steps, start=1)
            ],
        }

    def complete(self, state: dict) -> dict:
        current = state.get("workflow_execution", {})
        steps = current.get("steps", [])
        selected_path = state.get("selected_path")
        critic_issues = state.get("critic_issues", [])
        final_status = "completed" if selected_path == "complete" and not critic_issues else "repair_pending"
        updated_steps = []
        for index, step in enumerate(steps):
            status = "completed"
            if final_status != "completed" and index == len(steps) - 1:
                status = "blocked"
            updated_steps.append({**step, "status": status})
        return {
            "workflow_execution": {
                **current,
                "status": final_status,
                "steps": updated_steps,
                "selected_path": selected_path,
            }
        }

    def _active_reader_names(self, reader_results: list[dict]) -> list[str]:
        names: list[str] = []
        for item in reader_results:
            reader_name = item.get("reader")
            paths = item.get("paths", [])
            if reader_name and isinstance(paths, list) and paths:
                names.append(str(reader_name))
        return names
