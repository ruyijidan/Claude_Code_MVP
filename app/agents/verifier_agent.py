from __future__ import annotations

from typing import Any

from app.agents.base_agent import BaseAgent
from app.core.schema_validator import SchemaValidator
from app.core.tool_registry import ToolRegistry
from app.runtime.ecc_adapter import ECCAdapter


class VerifierAgent(BaseAgent):
    def __init__(self, spec, adapter: ECCAdapter | None = None, tool_registry: ToolRegistry | None = None) -> None:
        super().__init__(spec)
        self.adapter = adapter or ECCAdapter()
        self.validator = SchemaValidator()
        self.tool_registry = tool_registry

    def run(self, state: dict) -> dict:
        if self.tool_registry is not None:
            test_result = self.tool_registry.invoke("test_tool", repo_path=str(state["repo_path"]))
            code = test_result["returncode"]
            output = test_result["output"]
        else:
            code, output = self.adapter.run_tests(state["repo_path"])
        application_verification = self._verify_application_artifacts(state.get("repo_context", {}))
        result = {
            "changed_files": state.get("changed_files", []),
            "test_result": "passed" if code == 0 else "failed",
            "summary": "verification complete",
            "application_verification": application_verification,
        }
        errors = self.validator.validate_result(state["task_spec"], result)
        return {
            **result,
            "verification_errors": errors,
            "test_output": output,
        }

    def _verify_application_artifacts(self, repo_context: dict[str, Any]) -> dict[str, Any]:
        legibility = repo_context.get("application_legibility", {})
        artifact_summaries = legibility.get("artifact_summaries", [])
        if not isinstance(artifact_summaries, list):
            artifact_summaries = []

        findings: list[str] = []
        issues: list[str] = []
        checked_kinds: list[str] = []

        grouped_summaries = {
            "preview": [item for item in artifact_summaries if isinstance(item, dict) and item.get("kind") == "preview"],
            "log": [item for item in artifact_summaries if isinstance(item, dict) and item.get("kind") == "log"],
            "metric": [item for item in artifact_summaries if isinstance(item, dict) and item.get("kind") == "metric"],
        }

        if grouped_summaries["preview"]:
            checked_kinds.append("preview")
            findings.append(f"preview artifacts inspected: {self._summarize_paths(grouped_summaries['preview'])}")
        if grouped_summaries["log"]:
            checked_kinds.append("log")
            findings.append(f"log artifacts inspected: {self._summarize_paths(grouped_summaries['log'])}")
            issues.extend(self._log_issues(grouped_summaries["log"]))
        if grouped_summaries["metric"]:
            checked_kinds.append("metric")
            findings.append(f"metric artifacts inspected: {self._summarize_paths(grouped_summaries['metric'])}")
            issues.extend(self._metric_issues(grouped_summaries["metric"]))

        summary = "no application artifacts detected"
        if findings:
            summary = "; ".join(findings)

        return {
            "available": bool(findings),
            "checked_kinds": checked_kinds,
            "findings": findings,
            "issues": issues,
            "summary": summary,
        }

    def _summarize_paths(self, items: list[dict[str, Any]]) -> str:
        return ", ".join(str(item.get("path")) for item in items[:3] if item.get("path"))

    def _log_issues(self, items: list[dict[str, Any]]) -> list[str]:
        issues: list[str] = []
        for item in items:
            summary = str(item.get("summary", "")).lower()
            path = str(item.get("path", "log artifact"))
            if any(token in summary for token in ("traceback", "exception", "error", "failed")):
                issues.append(f"log artifact shows failure signal: {path}")
        return issues

    def _metric_issues(self, items: list[dict[str, Any]]) -> list[str]:
        issues: list[str] = []
        for item in items:
            summary = str(item.get("summary", "")).lower()
            path = str(item.get("path", "metric artifact"))
            if '"line_rate": 0' in summary or '"line_rate":0' in summary or "line-rate=\"0" in summary:
                issues.append(f"metric artifact shows zero line coverage: {path}")
        return issues
