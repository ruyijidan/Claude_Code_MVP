from __future__ import annotations

from app.agents.base_agent import BaseAgent
from app.core.schema_validator import SchemaValidator
from app.runtime.ecc_adapter import ECCAdapter


class VerifierAgent(BaseAgent):
    def __init__(self, spec, adapter: ECCAdapter | None = None) -> None:
        super().__init__(spec)
        self.adapter = adapter or ECCAdapter()
        self.validator = SchemaValidator()

    def run(self, state: dict) -> dict:
        code, output = self.adapter.run_tests(state["repo_path"])
        result = {
            "changed_files": state.get("changed_files", []),
            "test_result": "passed" if code == 0 else "failed",
            "summary": "verification complete",
        }
        errors = self.validator.validate_result(state["task_spec"], result)
        return {
            **result,
            "verification_errors": errors,
            "test_output": output,
        }
