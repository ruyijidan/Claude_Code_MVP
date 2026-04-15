from __future__ import annotations

import unittest

from app.superpowers.retry_policy import RetryPolicy


class RetryPolicyTests(unittest.TestCase):
    def test_retry_only_when_issues_exist(self) -> None:
        policy = RetryPolicy(max_attempts=3)
        self.assertTrue(policy.should_retry(1, ["tests_failed"]))
        self.assertFalse(policy.should_retry(3, ["tests_failed"]))
        self.assertFalse(policy.should_retry(1, []))


if __name__ == "__main__":
    unittest.main()
