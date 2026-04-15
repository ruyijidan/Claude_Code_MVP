from __future__ import annotations

from app.agents.base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    def run(self, state: dict) -> dict:
        request = state["request"]["feature_request"]
        return {
            "plan": [
                {"id": "analyze", "description": f"Analyze request: {request}", "agent": "planner"},
                {"id": "implement", "description": "Write feature code", "agent": "coder"},
                {"id": "verify", "description": "Run tests and validate outputs", "agent": "verifier"},
            ],
            "next_agent": "coder",
        }
