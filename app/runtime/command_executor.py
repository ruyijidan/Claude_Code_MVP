from __future__ import annotations

import subprocess
from pathlib import Path


class CommandExecutor:
    def run(self, cmd: list[str], cwd: Path) -> tuple[int, str]:
        completed = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        output = "\n".join(part for part in [completed.stdout, completed.stderr] if part).strip()
        return completed.returncode, output
