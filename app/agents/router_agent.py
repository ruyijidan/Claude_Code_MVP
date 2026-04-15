from __future__ import annotations

from app.agents.base_agent import BaseAgent


class RouterAgent(BaseAgent):
    def run(self, state: dict) -> dict:
        return {"selected_path": "repair" if state.get("critic_issues") else "complete"}
