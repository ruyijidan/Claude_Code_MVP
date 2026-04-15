from __future__ import annotations

from app.core.models import WorkflowSpec


class LightweightPlanner:
    WORKFLOW_NAME_MAP = {
        "fix_bug": "bugfix",
        "implement_feature": "implement-feature",
        "write_tests": "write-tests",
        "investigate_issue": "investigate-issue",
    }

    def infer_task_type(self, prompt: str) -> str:
        lowered = prompt.lower()
        if "investigate" in lowered or "debug why" in lowered:
            return "investigate_issue"
        if "test" in lowered and "write" in lowered:
            return "write_tests"
        if "fix" in lowered or "bug" in lowered or "failing" in lowered:
            return "fix_bug"
        return "implement_feature"

    def workflow_name_for_task_type(self, task_type: str) -> str:
        return self.WORKFLOW_NAME_MAP.get(task_type, "implement-feature")

    def build_plan(self, prompt: str, context: dict, task_type: str, workflow: WorkflowSpec | None = None) -> list[dict]:
        if workflow is not None:
            plan = []
            for index, step in enumerate(workflow.steps, start=1):
                plan.append(
                    {
                        "id": f"workflow_step_{index}",
                        "description": step,
                        "agent": "coding_loop",
                    }
                )
            return plan
        return [
            {
                "id": "context",
                "description": f"Inspect repository context for request: {prompt}",
                "agent": "coding_loop",
            },
            {
                "id": "implement",
                "description": f"Apply code changes for task type: {task_type}",
                "agent": "coding_loop",
            },
            {
                "id": "verify",
                "description": "Run tests and validate results",
                "agent": "coding_loop",
            },
        ]
