from __future__ import annotations

import os
from pathlib import Path

ENV_AUTH_PREFIXES = ("ANTHROPIC_",)


def _parse_env_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_env_lines(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in text.splitlines():
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
        parsed[key] = _parse_env_value(value)
    return parsed


def read_env_file(env_path: Path) -> dict[str, str]:
    if not env_path.exists():
        return {}
    return parse_env_lines(env_path.read_text(encoding="utf-8"))


def load_env_file(
    env_path: Path,
    *,
    override: bool = False,
    include_keys: set[str] | None = None,
    exclude_prefixes: tuple[str, ...] = (),
) -> dict[str, str]:
    loaded: dict[str, str] = {}
    for key, parsed in read_env_file(env_path).items():
        if include_keys is not None and key not in include_keys:
            continue
        if exclude_prefixes and key.startswith(exclude_prefixes):
            continue
        if override or key not in os.environ:
            os.environ[key] = parsed
        loaded[key] = os.environ[key]
    return loaded


def find_project_env(start_dir: Path | None = None) -> Path | None:
    current = (start_dir or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        env_path = candidate / ".env"
        if env_path.exists():
            return env_path
    return None


def load_project_env(
    start_dir: Path | None = None,
    *,
    override: bool = False,
    include_keys: set[str] | None = None,
    exclude_prefixes: tuple[str, ...] = (),
) -> tuple[Path | None, dict[str, str]]:
    env_path = find_project_env(start_dir)
    if env_path is None:
        return None, {}
    return env_path, load_env_file(
        env_path,
        override=override,
        include_keys=include_keys,
        exclude_prefixes=exclude_prefixes,
    )


def resolve_auth_loading_policy(start_dir: Path | None, explicit_provider: str | None, auth_source: str) -> tuple[str, tuple[str, ...]]:
    env_path = find_project_env(start_dir)
    env_values = read_env_file(env_path) if env_path is not None else {}
    selected_provider = (explicit_provider or env_values.get("SPEC_RUNTIME_PROVIDER") or os.getenv("SPEC_RUNTIME_PROVIDER") or "local").lower()
    if auth_source == "env":
        return selected_provider, ()
    if auth_source == "cli":
        return selected_provider, ENV_AUTH_PREFIXES
    if selected_provider in {"claude_code", "codex_cli"}:
        return selected_provider, ENV_AUTH_PREFIXES
    return selected_provider, ()
