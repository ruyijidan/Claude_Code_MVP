from __future__ import annotations

import os
from pathlib import Path


def _parse_env_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def load_env_file(env_path: Path, *, override: bool = False) -> dict[str, str]:
    loaded: dict[str, str] = {}
    if not env_path.exists():
        return loaded

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[len("export "):].strip()
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        if not key:
            continue
        parsed = _parse_env_value(value)
        if override or key not in os.environ:
            os.environ[key] = parsed
        loaded[key] = os.environ[key]
    return loaded


def load_project_env(start_dir: Path | None = None, *, override: bool = False) -> tuple[Path | None, dict[str, str]]:
    current = (start_dir or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        env_path = candidate / ".env"
        if env_path.exists():
            return env_path, load_env_file(env_path, override=override)
    return None, {}
