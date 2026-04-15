from __future__ import annotations

import sys
from shutil import which
from pathlib import Path

from app.runtime.command_executor import CommandExecutor
from app.runtime.patch_applier import PatchApplier


class ECCAdapter:
    provider_name = "mock"
    binary_name: str | None = None

    def __init__(self) -> None:
        self.command_executor = CommandExecutor()
        self.patch_applier = PatchApplier()

    def run_command(self, cmd: list[str], cwd: Path) -> tuple[int, str]:
        return self.command_executor.run(cmd, cwd)

    def edit_file(self, path: Path, content: str) -> None:
        self.patch_applier.write_text(path, content)

    def read_file(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def run_tests(self, target: Path) -> tuple[int, str]:
        return self.run_command([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=target)

    def provider_info(self) -> dict:
        binary_path = which(self.binary_name) if self.binary_name else None
        return {
            "provider": self.provider_name,
            "binary": self.binary_name,
            "binary_path": binary_path,
            "available": binary_path is not None or self.binary_name is None,
            "delegates_prompt": False,
        }

    def can_delegate_prompt(self) -> bool:
        return False

    def execute_prompt(self, prompt: str, cwd: Path, *, auto_approve: bool = False) -> tuple[int, str, list[str]]:
        return 1, f"provider '{self.provider_name}' does not support delegated prompt execution", []
