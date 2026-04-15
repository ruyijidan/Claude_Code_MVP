from __future__ import annotations

from app.agents.base_agent import BaseAgent


class CriticAgent(BaseAgent):
    def run(self, state: dict) -> dict:
        issues = []
        if state.get("test_result") != "passed":
            issues.append("tests_failed")
        if state.get("verification_errors"):
            issues.extend(state["verification_errors"])
        return {"critic_issues": issues}
