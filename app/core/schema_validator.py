from __future__ import annotations

from collections.abc import Mapping

from app.core.models import TaskSpec


class SchemaValidator:
    REQUIRED_RESULT_KEYS = {"changed_files", "test_result", "summary"}

    TYPE_CHECKS = {
        "string": str,
        "list": list,
        "dict": dict,
        "boolean": bool,
        "integer": int,
        "number": (int, float),
    }

    def validate_schema(self, payload: Mapping[str, object], schema: dict[str, str], *, label: str) -> list[str]:
        errors: list[str] = []
        for key, expected_type in schema.items():
            if key not in payload:
                errors.append(f"{label} missing key: {key}")
                continue
            expected_python_type = self.TYPE_CHECKS.get(expected_type)
            if expected_python_type is None:
                errors.append(f"{label} has unsupported schema type: {expected_type}")
                continue
            if not isinstance(payload[key], expected_python_type):
                errors.append(f"{label} key '{key}' must be a {expected_type}")
        return errors

    def validate_result(self, task_spec: TaskSpec, result: dict) -> list[str]:
        errors: list[str] = []
        missing = self.REQUIRED_RESULT_KEYS - set(result)
        if missing:
            errors.append(f"missing result keys: {sorted(missing)}")

        if not isinstance(result.get("changed_files", []), list):
            errors.append("changed_files must be a list")

        errors.extend(self.validate_schema(result, task_spec.outputs, label=f"{task_spec.name} result"))

        if "tests must pass" in " ".join(task_spec.done_when).lower():
            if result.get("test_result") != "passed":
                errors.append("tests did not pass")
        return errors
