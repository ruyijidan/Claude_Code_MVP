from __future__ import annotations

import re
from pathlib import Path

from app.core.models import ClarificationQuestion, IntentClarificationResult
from app.core.spec_loader import SpecLoader


class IntentClarifier:
    SHORT_CONTINUATIONS = {
        "ok",
        "okay",
        "continue",
        "go ahead",
        "sounds good",
        "好",
        "继续",
    }

    GENERIC_TARGETS = {
        "this",
        "that",
        "it",
        "thing",
        "stuff",
        "feature",
        "issue",
        "problem",
        "something",
    }

    TASK_VERBS = {
        "fix": "fix_bug",
        "bug": "fix_bug",
        "failing": "fix_bug",
        "error": "investigate_issue",
        "investigate": "investigate_issue",
        "debug": "investigate_issue",
        "write tests": "write_tests",
        "test": "write_tests",
        "add": "implement_feature",
        "implement": "implement_feature",
        "support": "implement_feature",
        "refactor": "implement_feature",
    }

    def __init__(self, spec_loader: SpecLoader | None = None) -> None:
        self.spec_loader = spec_loader

    def clarify(self, prompt: str, repo_path: Path, explicit_task_type: str | None = None) -> IntentClarificationResult:
        normalized_prompt = " ".join(prompt.split())
        inferred_task_type = explicit_task_type or self._infer_task_type(normalized_prompt)
        missing_constraints: list[str] = []
        questions: list[ClarificationQuestion] = []
        required_fields = self._required_fields_for_task_type(inferred_task_type)

        if normalized_prompt.lower() in self.SHORT_CONTINUATIONS:
            missing_constraints.append("continuation_context")
            questions.append(
                ClarificationQuestion(
                    key="continuation_context",
                    question="Which task should continue from here?",
                    reason="Short continuation input cannot be mapped to a single next step without prior turn state.",
                )
            )

        referenced_paths = self._extract_path_references(normalized_prompt)
        missing_paths = [path for path in referenced_paths if not (repo_path / path).exists()]
        if missing_paths:
            missing_constraints.append("repo_target")
            questions.append(
                ClarificationQuestion(
                    key="repo_target",
                    question=f"I could not find {missing_paths[0]!r} in the repository. Which existing file or module should be changed instead?",
                    reason="The request refers to a repo target that lightweight inspection could not find.",
                )
            )

        if "target" in required_fields and not self._has_target_signal(normalized_prompt, repo_path, inferred_task_type):
            missing_constraints.append("target")
            questions.append(
                ClarificationQuestion(
                    key="target",
                    question="Which file, module, feature, or failing behavior should this change focus on?",
                    reason="The request names an action but not a stable target for the first implementation pass.",
                )
            )

        if "success_criteria" in required_fields and not self._has_success_signal(normalized_prompt, inferred_task_type):
            missing_constraints.append("success_criteria")
            questions.append(
                ClarificationQuestion(
                    key="success_criteria",
                    question="What should count as success for this request?",
                    reason="The request does not yet describe a clear completion shape for planning and verification.",
                )
            )

        if missing_constraints:
            return IntentClarificationResult(
                status="needs_clarification",
                normalized_prompt=normalized_prompt,
                inferred_task_type=inferred_task_type,
                missing_constraints=self._dedupe(missing_constraints),
                questions=self._dedupe_questions(questions),
            )

        status = "normalized" if normalized_prompt != prompt else "ready"
        return IntentClarificationResult(
            status=status,
            normalized_prompt=normalized_prompt,
            inferred_task_type=inferred_task_type,
        )

    def _infer_task_type(self, prompt: str) -> str:
        lowered = prompt.lower()
        if "write tests" in lowered:
            return "write_tests"
        if "investigate" in lowered or "debug why" in lowered or "error" in lowered:
            return "investigate_issue"
        if "test" in lowered and "write" in lowered:
            return "write_tests"
        if "fix" in lowered or "bug" in lowered or "failing" in lowered:
            return "fix_bug"
        return "implement_feature"

    def _required_fields_for_task_type(self, task_type: str | None) -> set[str]:
        if task_type is None:
            return {"target", "success_criteria"}
        workflow_name_map = {
            "fix_bug": "bugfix",
            "implement_feature": "implement-feature",
            "write_tests": "write-tests",
            "investigate_issue": "investigate-issue",
        }
        if self.spec_loader is not None:
            workflow_name = workflow_name_map.get(task_type)
            if workflow_name is not None:
                workflow = self.spec_loader.load_workflow(workflow_name)
                if workflow.clarification_fields:
                    return set(workflow.clarification_fields)
        return {"target", "success_criteria"}

    def _extract_path_references(self, prompt: str) -> list[str]:
        matches = re.findall(r"(?<!\w)([\w./-]+\.[A-Za-z0-9]+)", prompt)
        return [match.strip("./") for match in matches if "/" in match or "." in match]

    def _has_target_signal(self, prompt: str, repo_path: Path, task_type: str | None) -> bool:
        lowered = prompt.lower()
        if self._extract_path_references(prompt):
            return True
        if task_type == "fix_bug" and any(token in lowered for token in ("failing test", "failing tests", "bug", "error", "traceback", "failure")):
            return True
        if task_type == "investigate_issue" and any(token in lowered for token in ("error", "traceback", "failure", "why", "issue")):
            return True
        if task_type == "write_tests" and "for " in lowered:
            return True
        if any(f" {token} " in f" {lowered} " for token in self.GENERIC_TARGETS):
            return False
        prompt_tokens = self._meaningful_tokens(lowered)
        if not prompt_tokens:
            return False
        repo_names = self._repo_name_signals(repo_path)
        if prompt_tokens & repo_names:
            return True
        if task_type == "implement_feature":
            return len(prompt_tokens) >= 2
        return False

    def _has_success_signal(self, prompt: str, task_type: str | None) -> bool:
        lowered = prompt.lower()
        if any(
            token in lowered
            for token in (
                "pass",
                "tests",
                "without",
                "exactly",
                "should",
                "so that",
                "support",
                "investigate",
                "why",
                "behavior",
            )
        ):
            return True
        if task_type == "fix_bug" and any(token in lowered for token in ("fix", "bug", "error", "failing")):
            return True
        if task_type == "write_tests" and "test" in lowered:
            return True
        if task_type == "investigate_issue" and any(token in lowered for token in ("investigate", "debug", "why")):
            return True
        if task_type == "implement_feature" and any(token in lowered for token in ("add", "implement", "support")):
            return True
        return False

    def _meaningful_tokens(self, prompt: str) -> set[str]:
        raw_tokens = re.findall(r"[a-zA-Z_]{3,}", prompt)
        stopwords = {
            "the",
            "and",
            "for",
            "with",
            "this",
            "that",
            "into",
            "from",
            "make",
            "please",
            "should",
            "tests",
            "test",
            "write",
            "fix",
            "add",
            "bug",
            "error",
        }
        return {token for token in raw_tokens if token not in stopwords}

    def _repo_name_signals(self, repo_path: Path) -> set[str]:
        names: set[str] = set()
        for path in repo_path.rglob("*"):
            if ".git" in path.parts or not path.is_file():
                continue
            names.add(path.stem.lower())
            names.update(part.lower() for part in path.parts if part not in (".", ".."))
            if len(names) > 2000:
                break
        return names

    def _dedupe(self, items: list[str]) -> list[str]:
        ordered: list[str] = []
        for item in items:
            if item not in ordered:
                ordered.append(item)
        return ordered

    def _dedupe_questions(self, questions: list[ClarificationQuestion]) -> list[ClarificationQuestion]:
        ordered: list[ClarificationQuestion] = []
        seen: set[str] = set()
        for question in questions:
            if question.key in seen:
                continue
            seen.add(question.key)
            ordered.append(question)
        return ordered
