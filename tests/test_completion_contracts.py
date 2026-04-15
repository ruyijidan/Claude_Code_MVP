from __future__ import annotations

import unittest

from app.agent.completion_contracts import CompletionContractRegistry


class CompletionContractTests(unittest.TestCase):
    def test_fix_bug_requires_changed_test_file(self) -> None:
        registry = CompletionContractRegistry()

        failed = registry.evaluate(
            "fix_bug",
            {
                "changed_files": ["sample_app/calculator.py"],
                "implementation_summary": "Updated the calculator logic.",
            },
        )
        passed = registry.evaluate(
            "fix_bug",
            {
                "changed_files": ["sample_app/calculator.py", "tests/test_calculator.py"],
                "implementation_summary": "Updated the calculator logic and regression coverage.",
            },
        )

        self.assertFalse(failed.passed)
        self.assertIn("requires at least one changed test file", failed.reasons[0])
        self.assertTrue(passed.passed)

    def test_generic_contract_requires_changes_and_summary(self) -> None:
        registry = CompletionContractRegistry()

        check = registry.evaluate("investigate_issue", {"changed_files": [], "summary": ""})

        self.assertFalse(check.passed)
        self.assertEqual(
            check.reasons,
            ["expected at least one changed file", "expected a non-empty summary"],
        )


if __name__ == "__main__":
    unittest.main()
