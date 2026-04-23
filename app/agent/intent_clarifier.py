from __future__ import annotations

import re
from pathlib import Path

from app.core.models import ClarificationQuestion, ContinuationCandidate, IntentClarificationResult
from app.core.spec_loader import SpecLoader


class IntentClarifier:
    MAX_CONTINUATION_CANDIDATES = 5

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
        return self.clarify_with_context(prompt, repo_path, explicit_task_type=explicit_task_type)

    def clarify_with_context(
        self,
        prompt: str,
        repo_path: Path,
        explicit_task_type: str | None = None,
        recent_run_summary: dict | None = None,
        recent_run_summaries: list[dict] | None = None,
    ) -> IntentClarificationResult:
        normalized_prompt = " ".join(prompt.split())
        continuation_summary = self._select_continuation_summary(
            normalized_prompt,
            repo_path,
            recent_run_summary=recent_run_summary,
            recent_run_summaries=recent_run_summaries,
        )
        continuation_candidates = self._build_continuation_candidates(
            repo_path,
            recent_run_summary=recent_run_summary,
            recent_run_summaries=recent_run_summaries,
        )
        continuation_target = self._infer_continuation_target(normalized_prompt, continuation_summary)
        effective_prompt = self._normalize_continuation_prompt(normalized_prompt, continuation_summary, continuation_target)
        inferred_task_type = explicit_task_type or self._infer_task_type(
            effective_prompt,
            continuation_summary if continuation_target is not None else None,
        )
        missing_constraints: list[str] = []
        questions: list[ClarificationQuestion] = []
        required_fields = self._required_fields_for_task_type(inferred_task_type)
        needs_continuation_context = False

        if self._has_ambiguous_continuation(normalized_prompt, repo_path, recent_run_summaries):
            needs_continuation_context = True
            candidate_labels = ", ".join(candidate.label for candidate in continuation_candidates)
            missing_constraints.append("continuation_context")
            questions.append(
                ClarificationQuestion(
                    key="continuation_context",
                    question=(
                        "I found multiple recent tasks in this repository. "
                        f"Which one should continue? Reply with one of: {candidate_labels}."
                    ),
                    reason=(
                        "Short continuation input matches more than one recent task, "
                        "so continuing automatically would be ambiguous."
                    ),
                )
            )

        if normalized_prompt.lower() in self.SHORT_CONTINUATIONS and continuation_target is None:
            needs_continuation_context = True
            missing_constraints.append("continuation_context")
            questions.append(
                ClarificationQuestion(
                    key="continuation_context",
                    question="Which task should continue from here?",
                    reason="Short continuation input cannot be mapped to a single next step without prior turn state.",
                )
            )

        if not needs_continuation_context:
            referenced_paths = self._extract_path_references(effective_prompt)
            missing_paths = []
            if not self._allows_new_path_references(effective_prompt):
                missing_paths = [path for path in referenced_paths if not (repo_path / path).exists()]
            if missing_paths:
                missing_constraints.append("repo_target")
                questions.append(
                    ClarificationQuestion(
                        key="repo_target",
                        question=(
                            f"I could not find {missing_paths[0]!r} in the repository. "
                            "Which existing file or module should be changed instead?"
                        ),
                        reason="The request refers to a repo target that lightweight inspection could not find.",
                    )
                )

            if "target" in required_fields and not self._has_target_signal(effective_prompt, repo_path, inferred_task_type):
                missing_constraints.append("target")
                questions.append(
                    ClarificationQuestion(
                        key="target",
                        question="Which file, module, feature, or failing behavior should this change focus on?",
                        reason="The request names an action but not a stable target for the first implementation pass.",
                    )
                )

            if "success_criteria" in required_fields and not self._has_success_signal(effective_prompt, inferred_task_type):
                missing_constraints.append("success_criteria")
                questions.append(
                    ClarificationQuestion(
                        key="success_criteria",
                        question="What should count as success for this request?",
                        reason="The request does not yet describe a clear completion shape for planning and verification.",
                    )
                )

        if missing_constraints:
            result_task_type = None if needs_continuation_context and explicit_task_type is None else inferred_task_type
            return IntentClarificationResult(
                status="needs_clarification",
                normalized_prompt=effective_prompt,
                inferred_task_type=result_task_type,
                continuation_candidates=continuation_candidates,
                missing_constraints=self._dedupe(missing_constraints),
                questions=self._dedupe_questions(questions),
            )

        status = "normalized" if normalized_prompt != prompt else "ready"
        if continuation_target is not None:
            status = "normalized"
        return IntentClarificationResult(
            status=status,
            normalized_prompt=effective_prompt,
            inferred_task_type=inferred_task_type,
            continuation_target=continuation_target,
            kickoff_message=self._build_kickoff_message(
                effective_prompt,
                inferred_task_type,
                repo_path,
                recent_run_summary=continuation_summary,
                continuation_target=continuation_target,
            ),
            continuation_candidates=continuation_candidates,
        )

    def _infer_task_type(self, prompt: str, recent_run_summary: dict | None = None) -> str:
        lowered = prompt.lower()
        if lowered in self.SHORT_CONTINUATIONS and recent_run_summary:
            recent_task = recent_run_summary.get("task")
            if isinstance(recent_task, str) and recent_task:
                return recent_task
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

    def _allows_new_path_references(self, prompt: str) -> bool:
        lowered = prompt.lower()
        return any(
            token in lowered
            for token in (
                "create ",
                "generate ",
                "produce ",
                "save ",
                "output ",
                "artifact",
                "artifacts",
            )
        )

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

    def _infer_continuation_target(self, prompt: str, recent_run_summary: dict | None = None) -> str | None:
        if (prompt.lower() in self.SHORT_CONTINUATIONS or self._is_continuation_label(prompt)) and recent_run_summary:
            recent_prompt = recent_run_summary.get("request_prompt")
            if isinstance(recent_prompt, str) and recent_prompt.strip():
                return recent_prompt.strip()
        return None

    def _select_continuation_summary(
        self,
        prompt: str,
        repo_path: Path,
        recent_run_summary: dict | None = None,
        recent_run_summaries: list[dict] | None = None,
    ) -> dict | None:
        if self._is_continuation_label(prompt):
            for index, candidate in enumerate(
                self._continuation_candidates(repo_path, recent_run_summary, recent_run_summaries),
                start=1,
            ):
                if prompt.lower() == f"recent_task_{index}":
                    return candidate
            return None
        if prompt.lower() not in self.SHORT_CONTINUATIONS:
            return recent_run_summary
        candidates = self._continuation_candidates(repo_path, recent_run_summary, recent_run_summaries)
        if len(candidates) == 1:
            return candidates[0]
        return None

    def _has_ambiguous_continuation(
        self,
        prompt: str,
        repo_path: Path,
        recent_run_summaries: list[dict] | None,
    ) -> bool:
        if prompt.lower() not in self.SHORT_CONTINUATIONS:
            return False
        return len(self._continuation_candidates(repo_path, None, recent_run_summaries)) > 1

    def _continuation_candidates(
        self,
        repo_path: Path,
        recent_run_summary: dict | None,
        recent_run_summaries: list[dict] | None,
    ) -> list[dict]:
        raw_candidates: list[dict] = []
        if recent_run_summaries:
            raw_candidates.extend(summary for summary in recent_run_summaries if isinstance(summary, dict))
        elif recent_run_summary:
            raw_candidates.append(recent_run_summary)

        normalized_repo_path = str(repo_path)
        unique_candidates: list[dict] = []
        seen_prompts: set[str] = set()
        for summary in raw_candidates:
            request_prompt = summary.get("request_prompt")
            request_repo_path = summary.get("request_repo_path")
            if not isinstance(request_prompt, str) or not request_prompt.strip():
                continue
            if isinstance(request_repo_path, str) and request_repo_path and request_repo_path != normalized_repo_path:
                continue
            prompt_key = request_prompt.strip()
            if prompt_key in seen_prompts:
                continue
            seen_prompts.add(prompt_key)
            unique_candidates.append(summary)
            if len(unique_candidates) >= self.MAX_CONTINUATION_CANDIDATES:
                break
        return unique_candidates

    def _build_continuation_candidates(
        self,
        repo_path: Path,
        recent_run_summary: dict | None,
        recent_run_summaries: list[dict] | None,
    ) -> list[ContinuationCandidate]:
        candidates: list[ContinuationCandidate] = []
        for index, summary in enumerate(
            self._continuation_candidates(repo_path, recent_run_summary, recent_run_summaries),
            start=1,
        ):
            request_prompt = summary.get("request_prompt")
            task_type = summary.get("task")
            candidates.append(
                ContinuationCandidate(
                    label=f"recent_task_{index}",
                    task_type=task_type if isinstance(task_type, str) else None,
                    request_prompt=request_prompt if isinstance(request_prompt, str) else None,
                    summary=self._continuation_summary(summary),
                    timestamp=self._continuation_timestamp(summary),
                )
            )
        return candidates

    def _is_continuation_label(self, prompt: str) -> bool:
        return re.fullmatch(r"recent_task_[1-9]\d*", prompt.lower()) is not None

    def _continuation_timestamp(self, recent_run_summary: dict) -> str | None:
        for key in ("completed_at", "created_at", "started_at", "timestamp", "run_id"):
            value = recent_run_summary.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    def _build_kickoff_message(
        self,
        prompt: str,
        task_type: str | None,
        repo_path: Path,
        recent_run_summary: dict | None = None,
        continuation_target: str | None = None,
    ) -> str | None:
        if continuation_target is not None and recent_run_summary is not None:
            summary = self._continuation_summary(recent_run_summary)
            if summary:
                return f"I'll continue the previous task by picking up {summary}."
            return "I'll continue the previous task from the latest confirmed execution context."
        target_hint = self._kickoff_target_hint(prompt, repo_path)
        if task_type == "fix_bug":
            if target_hint:
                return f"I'll inspect {target_hint} first, then apply the smallest fix and verify the result."
            return "I'll inspect the failing path first, then apply the smallest fix and verify the result."
        if task_type == "write_tests":
            if target_hint:
                return f"I'll inspect {target_hint} first, then add focused test coverage and run verification."
            return "I'll inspect the target area first, then add focused test coverage and run verification."
        if task_type == "investigate_issue":
            if target_hint:
                return f"I'll inspect {target_hint} first, then narrow down the cause before proposing or applying a fix."
            return "I'll inspect the reported issue first, then narrow down the cause before proposing or applying a fix."
        if target_hint:
            return f"I'll inspect {target_hint} first, then implement the requested change and verify the outcome."
        if prompt:
            return "I'll inspect the relevant code path first, then implement the request and verify the outcome."
        return None

    def _normalize_continuation_prompt(
        self,
        prompt: str,
        recent_run_summary: dict | None,
        continuation_target: str | None,
    ) -> str:
        if continuation_target is None or recent_run_summary is None:
            return prompt
        recent_prompt = recent_run_summary.get("request_prompt")
        if isinstance(recent_prompt, str) and recent_prompt.strip():
            return recent_prompt.strip()
        return prompt

    def _continuation_summary(self, recent_run_summary: dict) -> str | None:
        changed_files = recent_run_summary.get("changed_files")
        if isinstance(changed_files, list) and changed_files:
            return f"the last edited path around {changed_files[0]}"
        plan = recent_run_summary.get("plan")
        if isinstance(plan, list) and plan:
            first_step = plan[0]
            if isinstance(first_step, dict):
                description = first_step.get("description")
                if isinstance(description, str) and description:
                    return description
        recent_prompt = recent_run_summary.get("request_prompt")
        if isinstance(recent_prompt, str) and recent_prompt.strip():
            return f"the request '{recent_prompt.strip()}'"
        return None

    def _kickoff_target_hint(self, prompt: str, repo_path: Path) -> str | None:
        referenced_paths = self._extract_path_references(prompt)
        if referenced_paths:
            return referenced_paths[0]

        lowered = prompt.lower()
        repo_names = self._repo_name_signals(repo_path)
        for token in self._meaningful_tokens(lowered):
            if token in repo_names:
                return token
        return None
