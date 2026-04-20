from __future__ import annotations

import json
from pathlib import Path


ALLOWED_ACCEPTANCE_STATUSES = {"READY", "NEEDS_REVIEW", "BLOCKED"}


def validate_acceptance_report(payload: dict) -> None:
    required_keys = {
        "system_summary": str,
        "provider_risks": list,
        "live_acceptance_configured": bool,
        "acceptance_status": str,
        "evidence": list,
    }

    for key, expected_type in required_keys.items():
        if key not in payload:
            raise ValueError(f"missing required key: {key}")
        if not isinstance(payload[key], expected_type):
            raise ValueError(f"invalid type for {key}: expected {expected_type.__name__}")

    for list_key in ("provider_risks", "evidence"):
        if not all(isinstance(item, str) for item in payload[list_key]):
            raise ValueError(f"{list_key} must contain only strings")

    if payload["acceptance_status"] not in ALLOWED_ACCEPTANCE_STATUSES:
        raise ValueError(
            "invalid acceptance_status: "
            f"{payload['acceptance_status']!r}; expected one of {sorted(ALLOWED_ACCEPTANCE_STATUSES)}"
        )


def validate_acceptance_report_file(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_acceptance_report(payload)
    return payload
