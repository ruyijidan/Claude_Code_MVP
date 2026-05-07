from __future__ import annotations

from app.core.models import WorkflowSpec


class LightweightPlanner:
    TASK_TYPE_FALLBACK_WORKFLOW_NAMES = {
        "fix_bug": "bugfix",
        "implement_feature": "implement-feature",
        "write_tests": "write-tests",
        "investigate_issue": "investigate-issue",
    }

    def infer_task_type(self, prompt: str, workflows: list[WorkflowSpec] | None = None) -> str:
        if workflows is not None:
            matched_workflow = self._workflow_from_prompt(prompt, workflows)
            if matched_workflow is not None:
                return matched_workflow.task_type or matched_workflow.name.replace("-", "_")
        lowered = prompt.lower()
        if "investigate" in lowered or "debug why" in lowered:
            return "investigate_issue"
        if "test" in lowered and "write" in lowered:
            return "write_tests"
        if "fix" in lowered or "bug" in lowered or "failing" in lowered:
            return "fix_bug"
        return "implement_feature"

    def workflow_name_for_task_type(self, task_type: str, workflows: list[WorkflowSpec] | None = None) -> str:
        if workflows is not None:
            workflow = self._workflow_for_task_type(task_type, workflows)
            if workflow is not None:
                return workflow.workflow_slug or workflow.name
        return self.TASK_TYPE_FALLBACK_WORKFLOW_NAMES.get(task_type, task_type.replace("_", "-"))

    def build_plan(self, prompt: str, context: dict, task_type: str, workflow: WorkflowSpec | None = None) -> list[dict]:
        if workflow is not None:
            plan = []
            if workflow.required_context:
                context_summary = ", ".join(workflow.required_context[:4])
                focused_paths = self._focused_context_paths(context)
                plan.append(
                    {
                        "id": "workflow_context",
                        "description": self._context_description(context_summary, focused_paths),
                        "agent": "coding_loop",
                        "required_context": list(workflow.required_context),
                        "context_budget": context.get("context_budget", {}),
                        "focused_paths": focused_paths,
                    }
                )
            memory_hits = context.get("memory_hits", [])
            if memory_hits:
                plan.append(
                    {
                        "id": "workflow_memory",
                        "description": "reuse related trajectory context before exploring broader repo state",
                        "agent": "coding_loop",
                        "memory_hits": memory_hits[:3],
                        "memory_context_paths": list(context.get("memory_context_paths", [])),
                    }
                )
            application_legibility = context.get("application_legibility", {})
            artifact_kinds = self._available_legibility_kinds(application_legibility)
            if artifact_kinds:
                artifact_summary = ", ".join(artifact_kinds)
                plan.append(
                    {
                        "id": "workflow_legibility",
                        "description": f"inspect application artifacts before changes: {artifact_summary}",
                        "agent": "coding_loop",
                        "artifact_kinds": artifact_kinds,
                    }
                )
            if workflow.clarification_fields:
                clarification_summary = ", ".join(workflow.clarification_fields)
                plan.append(
                    {
                        "id": "workflow_clarification",
                        "description": f"respect workflow clarification fields: {clarification_summary}",
                        "agent": "coding_loop",
                        "clarification_fields": list(workflow.clarification_fields),
                    }
                )
            for index, step in enumerate(workflow.steps, start=1):
                plan.append(
                    {
                        "id": f"workflow_step_{index}",
                        "description": step,
                        "agent": "coding_loop",
                        "workflow": workflow.name,
                        "verification_targets": list(workflow.verification),
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

    def _available_legibility_kinds(self, legibility: dict) -> list[str]:
        available: list[str] = []
        if legibility.get("preview_targets"):
            available.append("preview targets")
        if legibility.get("log_files"):
            available.append("log files")
        if legibility.get("metric_files"):
            available.append("metric files")
        return available

    def _focused_context_paths(self, context: dict) -> list[str]:
        memory_paths = context.get("memory_context_paths", [])
        likely_paths = context.get("likely_relevant_files", [])
        focused: list[str] = []
        for collection in (memory_paths, likely_paths):
            if not isinstance(collection, list):
                continue
            for path in collection:
                if not isinstance(path, str) or path in focused:
                    continue
                focused.append(path)
                if len(focused) >= 6:
                    return focused
        return focused

    def _context_description(self, context_summary: str, focused_paths: list[str]) -> str:
        if not focused_paths:
            return f"assemble bounded context for workflow inputs: {context_summary}"
        focus_summary = ", ".join(focused_paths[:3])
        return f"assemble bounded context for workflow inputs: {context_summary}; prioritize {focus_summary}"

    def _workflow_for_task_type(self, task_type: str, workflows: list[WorkflowSpec]) -> WorkflowSpec | None:
        normalized_task_type = task_type.replace("-", "_")
        for workflow in workflows:
            workflow_task_type = workflow.task_type or workflow.name.replace("-", "_")
            if workflow_task_type == normalized_task_type:
                return workflow
        return None

    def _workflow_from_prompt(self, prompt: str, workflows: list[WorkflowSpec]) -> WorkflowSpec | None:
        lowered = prompt.lower()
        prompt_tokens = {token for token in lowered.replace("/", " ").replace(",", " ").split() if len(token) >= 3}
        for workflow in workflows:
            if self._workflow_matches_prompt(workflow, lowered, prompt_tokens):
                return workflow
        return None

    def _workflow_matches_prompt(self, workflow: WorkflowSpec, lowered_prompt: str, prompt_tokens: set[str]) -> bool:
        for signal in workflow.entry_signals:
            lowered_signal = signal.lower()
            if "prompt contains" in lowered_signal:
                signal_text = lowered_signal.split("prompt contains", maxsplit=1)[1]
                signal_tokens = {token.strip(" ,") for token in signal_text.replace("/", " ").split() if len(token.strip(" ,")) >= 3}
                if signal_tokens and signal_tokens.intersection(prompt_tokens):
                    return True
            elif "task type inferred as" in lowered_signal:
                continue
            elif lowered_signal in lowered_prompt:
                return True
        return False
