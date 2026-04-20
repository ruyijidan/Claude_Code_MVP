#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_LIVE_TESTS="${CC_RUN_LIVE_PROVIDER_TESTS:-0}"
RUN_LONG_TASK="${CC_RUN_LIVE_ACCEPTANCE_TASK:-0}"
LIVE_TIMEOUT_SECONDS="${CC_ACCEPTANCE_TIMEOUT_SECONDS:-600}"
LIVE_CLI_PROVIDER="${CC_LIVE_CLI_PROVIDER:-}"
LIVE_API_PROVIDER="${CC_LIVE_API_PROVIDER:-}"
TASK_PROVIDER="${CC_ACCEPTANCE_PROVIDER:-${LIVE_CLI_PROVIDER}}"
TASK_AUTH_SOURCE="${CC_ACCEPTANCE_AUTH_SOURCE:-auto}"
TASK_TEMPLATE_PATH="${CC_ACCEPTANCE_TEMPLATE_PATH:-$ROOT_DIR/specs/templates/acceptance-task-template.md}"
TASK_PROMPT="${CC_ACCEPTANCE_PROMPT:-}"
REPORT_MARKDOWN_RELATIVE_PATH=".claude-code/acceptance/final_acceptance_report.md"
REPORT_JSON_RELATIVE_PATH=".claude-code/acceptance/final_acceptance_report.json"

run_with_optional_timeout() {
  local seconds="$1"
  shift
  if command -v timeout >/dev/null 2>&1; then
    timeout "$seconds" "$@"
  else
    "$@"
  fi
}

prepare_acceptance_workspace() {
  local target_dir="$1"
  mkdir -p "$target_dir"
  rsync -rlt --delete \
    --exclude '.git' \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude 'logs' \
    "$ROOT_DIR"/ "$target_dir"/ >/dev/null
}

render_acceptance_prompt() {
  local template_path="$1"
  local timeout_seconds="$2"
  local timeout_minutes="$((timeout_seconds / 60))"
  python3 - "$template_path" "$timeout_minutes" "$REPORT_MARKDOWN_RELATIVE_PATH" "$REPORT_JSON_RELATIVE_PATH" <<'PY'
from pathlib import Path
import sys

template_path = Path(sys.argv[1])
timeout_minutes = sys.argv[2]
report_markdown_path = sys.argv[3]
report_json_path = sys.argv[4]
template = template_path.read_text(encoding="utf-8")
print(
    template.format(
        timeout_minutes=timeout_minutes,
        report_markdown_path=report_markdown_path,
        report_json_path=report_json_path,
    )
)
PY
}

validate_acceptance_report_json() {
  local json_path="$1"
  python3 - "$json_path" <<'PY'
from pathlib import Path
import json
import sys

json_path = Path(sys.argv[1])
payload = json.loads(json_path.read_text(encoding="utf-8"))
required_keys = {
    "system_summary": str,
    "provider_risks": list,
    "live_acceptance_configured": bool,
    "acceptance_status": str,
    "evidence": list,
}

for key, expected_type in required_keys.items():
    if key not in payload:
        raise SystemExit(f"missing required key: {key}")
    if not isinstance(payload[key], expected_type):
        raise SystemExit(f"invalid type for {key}: expected {expected_type.__name__}")

for list_key in ("provider_risks", "evidence"):
    if not all(isinstance(item, str) for item in payload[list_key]):
        raise SystemExit(f"{list_key} must contain only strings")

allowed_statuses = {"READY", "NEEDS_REVIEW", "BLOCKED"}
if payload["acceptance_status"] not in allowed_statuses:
    raise SystemExit(
        "invalid acceptance_status: "
        f"{payload['acceptance_status']!r}; expected one of {sorted(allowed_statuses)}"
    )

print(f"validated acceptance report: {payload['acceptance_status']}")
PY
}

echo "==> Running default fast acceptance checks"
python3 -m unittest discover -s "$ROOT_DIR/tests"
bash "$ROOT_DIR/scripts/agent_verify.sh"

if [[ "$RUN_LIVE_TESTS" == "1" || "$RUN_LIVE_TESTS" == "true" || "$RUN_LIVE_TESTS" == "yes" || "$RUN_LIVE_TESTS" == "on" ]]; then
  echo "==> Running live provider integration checks"
  (
    cd "$ROOT_DIR"
    python3 -m unittest tests.test_live_provider_integration
  )
fi

if [[ "$RUN_LONG_TASK" == "1" || "$RUN_LONG_TASK" == "true" || "$RUN_LONG_TASK" == "yes" || "$RUN_LONG_TASK" == "on" ]]; then
  if [[ -z "$TASK_PROVIDER" ]]; then
    echo "❌ CC_ACCEPTANCE_PROVIDER or CC_LIVE_CLI_PROVIDER is required for the long acceptance task"
    exit 1
  fi

  ACCEPTANCE_DIR="/tmp/claude-code-mvp-release-acceptance-$(date +%s)"
  mkdir -p "$ACCEPTANCE_DIR"
  trap 'rm -rf "$ACCEPTANCE_DIR"' EXIT

  echo "==> Preparing isolated acceptance workspace: $ACCEPTANCE_DIR"
  prepare_acceptance_workspace "$ACCEPTANCE_DIR/repo"

  if [[ -z "$TASK_PROMPT" ]]; then
    TASK_PROMPT="$(render_acceptance_prompt "$TASK_TEMPLATE_PATH" "$LIVE_TIMEOUT_SECONDS")"
  fi

  echo "==> Running autonomous live acceptance task with provider: $TASK_PROVIDER"
  (
    cd "$ROOT_DIR"
    run_with_optional_timeout "$LIVE_TIMEOUT_SECONDS" \
      python3 -m app.cli.main "$TASK_PROMPT" \
      --repo "$ACCEPTANCE_DIR/repo" \
      --provider "$TASK_PROVIDER" \
      --auth-source "$TASK_AUTH_SOURCE" \
      --delegate-to-provider \
      --auto-approve \
      --dangerously-skip-confirmation \
      --json > "$ACCEPTANCE_DIR/live_acceptance_result.json"
  )

  REPORT_PATH="$ACCEPTANCE_DIR/repo/$REPORT_MARKDOWN_RELATIVE_PATH"
  REPORT_JSON_PATH="$ACCEPTANCE_DIR/repo/$REPORT_JSON_RELATIVE_PATH"
  if [[ -f "$REPORT_PATH" && -f "$REPORT_JSON_PATH" ]]; then
    echo "==> Live acceptance artifacts created:"
    echo "$REPORT_PATH"
    echo "$REPORT_JSON_PATH"
    echo "==> Validating acceptance JSON contract"
    validate_acceptance_report_json "$REPORT_JSON_PATH"
  else
    echo "❌ Expected acceptance artifacts were not created"
    echo "Markdown path: $REPORT_PATH"
    echo "JSON path: $REPORT_JSON_PATH"
    echo "Live result payload:"
    cat "$ACCEPTANCE_DIR/live_acceptance_result.json"
    exit 1
  fi
fi

echo "✅ Release acceptance checks completed"
