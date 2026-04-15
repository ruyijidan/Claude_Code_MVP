from __future__ import annotations

import unittest

from app.evals.evaluator import Evaluator


class EvaluatorTests(unittest.TestCase):
    def test_score_success_and_failure(self) -> None:
        evaluator = Evaluator()
        self.assertEqual(evaluator.score({"test_result": "passed", "verification_errors": []})["score"], 1.0)
        self.assertEqual(evaluator.score({"test_result": "failed", "verification_errors": ["x"]})["score"], 0.0)

    def test_score_accounts_for_gate_and_completion_failures(self) -> None:
        evaluator = Evaluator()

        result = evaluator.score(
            {
                "test_result": "passed",
                "verification_errors": [],
                "gate_failures": ["completion contract failed"],
                "completion_check": {"passed": False},
            }
        )

        self.assertEqual(result["score"], 0.0)


if __name__ == "__main__":
    unittest.main()
