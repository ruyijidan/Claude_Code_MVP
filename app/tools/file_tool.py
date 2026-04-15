from __future__ import annotations

from pathlib import Path

from app.tools.base_tool import BaseTool


class FileTool(BaseTool):
    name = "file_tool"

    def invoke(self, path: str) -> dict:
        file_path = Path(path)
        return {
            "path": path,
            "exists": file_path.exists(),
            "content": file_path.read_text(encoding="utf-8") if file_path.exists() else "",
        }
