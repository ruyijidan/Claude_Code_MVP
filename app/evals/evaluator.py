from __future__ import annotations


class Evaluator:
    def score(self, state: dict) -> dict:
        score = 1.0
        if state.get("test_result") != "passed":
            score -= 0.5
        if state.get("verification_errors"):
            score -= 0.5
        if state.get("gate_failures"):
            score -= 0.5
        completion_check = state.get("completion_check", {})
        if completion_check and not completion_check.get("passed", True):
            score -= 0.5
        return {"score": max(score, 0.0)}
