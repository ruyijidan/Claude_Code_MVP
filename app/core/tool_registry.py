from __future__ import annotations

from app.core.models import ToolSpec
from app.core.schema_validator import SchemaValidator
from app.tools.base_tool import BaseTool


class ToolRegistry:
    def __init__(self, tool_specs: list[ToolSpec], validator: SchemaValidator | None = None) -> None:
        self.validator = validator or SchemaValidator()
        self.specs = {spec.name: spec for spec in tool_specs}
        self.tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if tool.name not in self.specs:
            raise KeyError(f"unknown tool spec: {tool.name}")
        self.tools[tool.name] = tool

    def describe_many(self, names: list[str]) -> list[dict[str, object]]:
        descriptions: list[dict[str, object]] = []
        for name in names:
            spec = self.specs.get(name)
            if spec is None:
                continue
            descriptions.append(
                {
                    "name": spec.name,
                    "description": spec.description,
                    "input_schema": dict(spec.input_schema),
                    "output_schema": dict(spec.output_schema),
                }
            )
        return descriptions

    def invoke(self, name: str, **kwargs) -> dict:
        spec = self.specs.get(name)
        if spec is None:
            raise KeyError(f"unknown tool: {name}")
        tool = self.tools.get(name)
        if tool is None:
            raise KeyError(f"tool not registered: {name}")
        input_errors = self.validator.validate_schema(kwargs, spec.input_schema, label=f"{name} input")
        if input_errors:
            raise ValueError("; ".join(input_errors))
        result = tool.invoke(**kwargs)
        output_errors = self.validator.validate_schema(result, spec.output_schema, label=f"{name} output")
        if output_errors:
            raise ValueError("; ".join(output_errors))
        return result
