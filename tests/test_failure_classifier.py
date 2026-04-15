from __future__ import annotations

import unittest

from app.superpowers.failure_classifier import FailureClassifier


class FailureClassifierTests(unittest.TestCase):
    def test_classifies_missing_tests_and_architecture_violations(self) -> None:
        classifier = FailureClassifier()

        signals = classifier.classify(
            {"changed_files": ["sample_app/calculator.py"]},
            [
                "fix_bug requires at least one changed test file",
                "architecture boundary violation detected",
            ],
        )

        kinds = {signal.kind for signal in signals}
        self.assertIn("missing_tests", kinds)
        self.assertIn("architecture_violation", kinds)

    def test_classifies_no_effect_change(self) -> None:
        classifier = FailureClassifier()

        signals = classifier.classify({"changed_files": []}, [])

        self.assertEqual(signals[0].kind, "no_effect_change")


if __name__ == "__main__":
    unittest.main()
