from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show local Codex token usage from ~/.codex session logs."
    )
    parser.add_argument(
        "--codex-home",
        default=str(Path.home() / ".codex"),
        help="Path to the Codex home directory. Default: ~/.codex",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Show a one-line summary for every local session file.",
    )
    return parser.parse_args()


def iter_session_files(codex_home: Path) -> list[Path]:
    sessions_dir = codex_home / "sessions"
    if not sessions_dir.exists():
        return []
    return sorted(sessions_dir.rglob("*.jsonl"))


def load_latest_token_info(session_file: Path) -> dict[str, Any] | None:
    latest: dict[str, Any] | None = None
    for line in session_file.read_text(encoding="utf-8").splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (
            payload.get("type") == "event_msg"
            and payload.get("payload", {}).get("type") == "token_count"
        ):
            token_payload = payload["payload"]
            latest = dict(token_payload.get("info") or {})
            latest["rate_limits"] = token_payload.get("rate_limits") or {}
    return latest


def load_session_id(session_file: Path) -> str:
    for line in session_file.read_text(encoding="utf-8").splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("type") == "session_meta":
            return payload.get("payload", {}).get("id", session_file.stem)
    return session_file.stem


def format_reset(ts: int | None) -> str:
    if not ts:
        return "unknown"
    return datetime.fromtimestamp(ts).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def print_summary_line(session_file: Path, token_info: dict[str, Any]) -> None:
    usage = token_info["total_token_usage"]
    rate_limits = token_info.get("rate_limits") or {}
    primary = rate_limits.get("primary") or {}
    secondary = rate_limits.get("secondary") or {}
    session_id = load_session_id(session_file)
    five_hour_remaining = 100 - float(primary.get("used_percent", 0))
    weekly_remaining = 100 - float(secondary.get("used_percent", 0))
    print(
        f"{session_file.name} | session_id={session_id} | total_tokens={usage['total_tokens']} "
        f"| 5h_remaining={five_hour_remaining:.0f}% | weekly_remaining={weekly_remaining:.0f}%"
    )


def print_detailed_report(session_file: Path, token_info: dict[str, Any]) -> None:
    total = token_info["total_token_usage"]
    last = token_info["last_token_usage"]
    rate_limits = token_info.get("rate_limits") or {}
    primary = rate_limits.get("primary") or {}
    secondary = rate_limits.get("secondary") or {}

    print(f"session_file: {session_file}")
    print(f"plan_type: {rate_limits.get('plan_type', 'unknown')}")
    print(f"session_id: {load_session_id(session_file)}")
    print()
    print("total_token_usage:")
    print(f"  input_tokens: {total['input_tokens']}")
    print(f"  cached_input_tokens: {total['cached_input_tokens']}")
    print(f"  output_tokens: {total['output_tokens']}")
    print(f"  reasoning_output_tokens: {total['reasoning_output_tokens']}")
    print(f"  total_tokens: {total['total_tokens']}")
    print()
    print("last_token_usage:")
    print(f"  input_tokens: {last['input_tokens']}")
    print(f"  cached_input_tokens: {last['cached_input_tokens']}")
    print(f"  output_tokens: {last['output_tokens']}")
    print(f"  reasoning_output_tokens: {last['reasoning_output_tokens']}")
    print(f"  total_tokens: {last['total_tokens']}")
    print()
    print("rate_limits:")
    print(f"  5h used: {primary.get('used_percent', 'unknown')}%")
    if "used_percent" in primary:
        print(f"  5h remaining: {100 - float(primary['used_percent']):.0f}%")
    print(f"  5h resets_at: {format_reset(primary.get('resets_at'))}")
    print(f"  weekly used: {secondary.get('used_percent', 'unknown')}%")
    if "used_percent" in secondary:
        print(f"  weekly remaining: {100 - float(secondary['used_percent']):.0f}%")
    print(f"  weekly resets_at: {format_reset(secondary.get('resets_at'))}")


def main() -> int:
    args = parse_args()
    codex_home = Path(args.codex_home).expanduser()
    session_files = iter_session_files(codex_home)

    if not session_files:
        print(f"No session files found under {codex_home / 'sessions'}")
        return 1

    if args.all:
        found_any = False
        for session_file in session_files:
            token_info = load_latest_token_info(session_file)
            if token_info is None:
                continue
            print_summary_line(session_file, token_info)
            found_any = True
        if not found_any:
            print("No token_count events found in local session files.")
            return 1
        return 0

    latest_file = session_files[-1]
    token_info = load_latest_token_info(latest_file)
    if token_info is None:
        print(f"No token_count event found in latest session: {latest_file}")
        return 1

    print_detailed_report(latest_file, token_info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
