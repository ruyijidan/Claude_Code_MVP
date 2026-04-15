from __future__ import annotations


class RetryPolicy:
    def __init__(self, max_attempts: int = 2) -> None:
        self.max_attempts = max_attempts

    def should_retry(self, attempt: int, issues: list[str]) -> bool:
        return bool(issues) and attempt < self.max_attempts
