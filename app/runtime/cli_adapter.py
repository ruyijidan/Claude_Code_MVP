from __future__ import annotations

from pathlib import Path

from app.runtime.local_runtime import LocalRuntimeAdapter


class ClaudeCodeAdapter(LocalRuntimeAdapter):
    provider_name = "claude_code"
    binary_name = "claude"

    def provider_info(self) -> dict:
        info = super().provider_info()
        info["delegates_prompt"] = info["available"]
        return info

    def can_delegate_prompt(self) -> bool:
        return self.provider_info()["available"]

    def execute_prompt(self, prompt: str, cwd: Path, *, auto_approve: bool = False) -> tuple[int, str, list[str]]:
        cmd = [
            "claude",
            "-p",
            "--output-format",
            "json",
            "--dangerously-skip-permissions" if auto_approve else "--permission-mode",
        ]
        if auto_approve:
            cmd.append(prompt)
        else:
            cmd.extend(["acceptEdits", prompt])
        code, output = self.run_command(cmd, cwd)
        return code, output, cmd


class CodexCLIAdapter(LocalRuntimeAdapter):
    provider_name = "codex_cli"
    binary_name = "codex"

    def provider_info(self) -> dict:
        info = super().provider_info()
        info["delegates_prompt"] = info["available"]
        return info

    def can_delegate_prompt(self) -> bool:
        return self.provider_info()["available"]

    def execute_prompt(self, prompt: str, cwd: Path, *, auto_approve: bool = False) -> tuple[int, str, list[str]]:
        cmd = [
            "codex",
            "--cd",
            str(cwd),
            "exec",
            "--json",
            "--skip-git-repo-check",
        ]
        if auto_approve:
            cmd.extend(["--dangerously-bypass-approvals-and-sandbox"])
        else:
            cmd.extend(["--full-auto"])
        cmd.append(prompt)
        code, output = self.run_command(cmd, cwd)
        return code, output, cmd
