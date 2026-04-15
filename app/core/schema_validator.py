from __future__ import annotations

from app.core.models import TaskSpec


class SchemaValidator:
    REQUIRED_RESULT_KEYS = {"changed_files", "test_result", "summary"}

    def validate_result(self, task_spec: TaskSpec, result: dict) -> list[str]:
        errors: list[str] = []
        missing = self.REQUIRED_RESULT_KEYS - set(result)
        if missing:
            errors.append(f"missing result keys: {sorted(missing)}")

        if not isinstance(result.get("changed_files", []), list):
            errors.append("changed_files must be a list")

        if "tests must pass" in " ".join(task_spec.done_when).lower():
            if result.get("test_result") != "passed":
                errors.append("tests did not pass")
        return errors
