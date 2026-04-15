from __future__ import annotations


class LightweightPlanner:
    def infer_task_type(self, prompt: str) -> str:
        lowered = prompt.lower()
        if "investigate" in lowered or "debug why" in lowered:
            return "investigate_issue"
        if "test" in lowered and "write" in lowered:
            return "write_tests"
        if "fix" in lowered or "bug" in lowered or "failing" in lowered:
            return "fix_bug"
        return "implement_feature"

    def build_plan(self, prompt: str, context: dict, task_type: str) -> list[dict]:
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
