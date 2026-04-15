from __future__ import annotations


class GraphBuilder:
    def build_default_graph(self) -> list[str]:
        return ["planner", "coder", "verifier", "critic", "router"]
