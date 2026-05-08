#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DURATION_MINUTES="${LONG_TASK_GAME_DURATION_MINUTES:-30}"
DURATION_SECONDS="${LONG_TASK_GAME_DURATION_SECONDS:-$((DURATION_MINUTES * 60))}"
ITERATION_BUDGET_SECONDS="${LONG_TASK_GAME_ITERATION_SECONDS:-600}"
PROVIDER="${LONG_TASK_GAME_PROVIDER:-glm5}"
AUTH_SOURCE="${LONG_TASK_GAME_AUTH_SOURCE:-auto}"
REPO_PATH="${LONG_TASK_GAME_REPO:-$ROOT_DIR}"
GAME_NAME="${LONG_TASK_GAME_NAME:-Halo Drift / 环轨漂移}"
GAME_PATH="${LONG_TASK_GAME_PATH:-examples/halo-drift}"
TASK_TYPE="${LONG_TASK_GAME_TASK_TYPE:-long_task_game}"
RUN_MODE="${LONG_TASK_GAME_RUN_MODE:-marathon}"
DIFFICULTY="${LONG_TASK_GAME_DIFFICULTY:-standard}"
KEEP_ARTIFACTS="${LONG_TASK_GAME_KEEP_ARTIFACTS:-0}"
LOG_DIR="${LONG_TASK_GAME_LOG_DIR:-$ROOT_DIR/.claude-code/long-task-game-sessions}"
SESSION_ID="$(date -u +%Y%m%d-%H%M%S)"
SESSION_DIR="${LONG_TASK_GAME_SESSION_DIR:-$LOG_DIR/$SESSION_ID}"
LOG_PATH="${LONG_TASK_GAME_LOG_PATH:-$LOG_DIR/$SESSION_ID.md}"
RESULT_JSON_PATH="${LONG_TASK_GAME_RESULT_JSON:-$LOG_DIR/$SESSION_ID.result.json}"
TARGET_ABS_PATH="$REPO_PATH/$GAME_PATH"
VERIFY_COMMAND="${LONG_TASK_GAME_VERIFY_COMMAND:-node --check $TARGET_ABS_PATH/game.js}"

run_with_optional_timeout() {
  local seconds="$1"
  shift
  if command -v timeout >/dev/null 2>&1; then
    timeout "$seconds" "$@"
  else
    "$@"
  fi
}

run_with_spinner() {
  local label="$1"
  local output_path="$2"
  shift 2

  local spinner='|/-\'
  local index=0
  local start_epoch
  start_epoch="$(utc_now_epoch)"

  "$@" > "$output_path" 2>&1 &
  local child_pid=$!

  while kill -0 "$child_pid" 2>/dev/null; do
    local now_epoch
    now_epoch="$(utc_now_epoch)"
    local elapsed_seconds=$((now_epoch - start_epoch))
    if (( elapsed_seconds < 0 )); then
      elapsed_seconds=0
    fi
    local elapsed_minute=$((elapsed_seconds / 60))
    local elapsed_second=$((elapsed_seconds % 60))
    printf '\r==> %s [%s] %02d:%02d' "$label" "${spinner:index % 4:1}" "$elapsed_minute" "$elapsed_second"
    index=$((index + 1))
    sleep 1
  done

  wait "$child_pid"
  local exit_code=$?
  local total_elapsed
  total_elapsed="$(python3 - "$start_epoch" <<'PY'
from datetime import datetime, timezone
import sys

start_epoch = int(sys.argv[1])
end_epoch = int(datetime.now(timezone.utc).timestamp())
elapsed_seconds = max(end_epoch - start_epoch, 0)
minutes = elapsed_seconds // 60
seconds = elapsed_seconds % 60
print(f"{minutes:02d}:{seconds:02d}")
PY
)"
  printf '\r==> %s [done %s]\n' "$label" "$total_elapsed"
  return "$exit_code"
}

utc_now_iso() {
  python3 - <<'PY'
from datetime import datetime, timezone
print(datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
PY
}

utc_now_epoch() {
  python3 - <<'PY'
from datetime import datetime, timezone
print(int(datetime.now(timezone.utc).timestamp()))
PY
}

write_session_log() {
  local actual_end="$1"
  local elapsed="$2"
  local sustained_target="$3"
  local verification_result="$4"
  local notes="$5"
  local iteration_count="$6"
  local drift_observed="$7"
  local session_blocks_path="$8"
  python3 - "$LOG_PATH" "$DURATION_MINUTES" "$START_ISO" "$PLANNED_END_ISO" "$actual_end" "$elapsed" "$sustained_target" "$PROVIDER" "$GAME_NAME" "$GAME_PATH" "$RUN_MODE" "$DIFFICULTY" "$VERIFY_COMMAND" "$verification_result" "$notes" "$iteration_count" "$drift_observed" "$session_blocks_path" <<'PY'
from pathlib import Path
import sys

log_path = Path(sys.argv[1])
requested_minutes = sys.argv[2]
start_iso = sys.argv[3]
planned_end_iso = sys.argv[4]
actual_end_iso = sys.argv[5]
elapsed = sys.argv[6]
sustained_target = sys.argv[7]
provider = sys.argv[8]
game_name = sys.argv[9]
game_path = sys.argv[10]
run_mode = sys.argv[11]
difficulty = sys.argv[12]
verify_command = sys.argv[13]
verification_result = sys.argv[14]
notes = sys.argv[15]
iteration_count = sys.argv[16]
drift_observed = sys.argv[17]
session_blocks_path = Path(sys.argv[18])
session_blocks = session_blocks_path.read_text(encoding="utf-8") if session_blocks_path.exists() else ""

content = f"""---
last_updated: {start_iso[:10]}
status: active
owner: core
---

# Long Task Game Session Log / 长任务小游戏会话日志

## Target Duration / 目标时长

- requested: {requested_minutes} minutes
- planned start: {start_iso}
- planned end: {planned_end_iso}

## Observed Run / 实际运行

- actual start: {start_iso}
- actual end: {actual_end_iso}
- elapsed: {elapsed}
- provider or execution path: {provider}

## Artifact / 产物

- target game: {game_name}
- artifact path: {game_path}
- run mode: {run_mode}
- difficulty: {difficulty}

## Iteration Summary / 迭代摘要

- iterations: {iteration_count}
- drift observed: {drift_observed}

## Iteration Log / 迭代记录

{session_blocks}
## Verification / 验证

- commands run: {verify_command}
- result: {verification_result}
- notes: {notes}

## Outcome / 结果

- sustained target duration: {sustained_target}
- major upgrades made: pending
- whether the run preserved or replaced an artifact: pending
"""
log_path.parent.mkdir(parents=True, exist_ok=True)
log_path.write_text(content, encoding="utf-8")
PY
}

write_summary_json() {
  local actual_end="$1"
  local elapsed_seconds="$2"
  local sustained_target="$3"
  local verification_result="$4"
  local iteration_count="$5"
  local drift_observed="$6"
  local last_iteration_json="$7"
  local provider_path="$8"
  python3 - "$RESULT_JSON_PATH" "$SESSION_ID" "$START_ISO" "$actual_end" "$elapsed_seconds" "$DURATION_SECONDS" "$DURATION_MINUTES" "$sustained_target" "$verification_result" "$iteration_count" "$drift_observed" "$last_iteration_json" "$provider_path" "$GAME_PATH" "$TASK_TYPE" "$RUN_MODE" "$DIFFICULTY" <<'PY'
from pathlib import Path
import json
import sys

result_path = Path(sys.argv[1])
payload = {
    "session_id": sys.argv[2],
    "actual_start": sys.argv[3],
    "actual_end": sys.argv[4],
    "elapsed_seconds": int(sys.argv[5]),
    "requested_seconds": int(sys.argv[6]),
    "requested_minutes": int(sys.argv[7]),
    "sustained_target_duration": sys.argv[8],
    "verification_result": sys.argv[9],
    "iteration_count": int(sys.argv[10]),
    "drift_observed": sys.argv[11],
    "last_iteration_json": sys.argv[12],
    "provider_or_execution_path": sys.argv[13],
    "artifact_path": sys.argv[14],
    "task_type": sys.argv[15],
    "run_mode": sys.argv[16],
    "difficulty": sys.argv[17],
}
result_path.parent.mkdir(parents=True, exist_ok=True)
result_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
PY
}

build_iteration_prompt() {
  local iteration="$1"
  local remaining_seconds="$2"
  local previous_result_json="$3"
  local drift_note="$4"
  python3 - "$iteration" "$remaining_seconds" "$previous_result_json" "$REPO_PATH" "$GAME_PATH" "$GAME_NAME" "$DURATION_MINUTES" "$TASK_TYPE" "$drift_note" <<'PY'
from pathlib import Path
import json
import sys

iteration = sys.argv[1]
remaining_seconds = sys.argv[2]
previous_result_json = Path(sys.argv[3])
repo_path = sys.argv[4]
game_path = sys.argv[5]
game_name = sys.argv[6]
duration_minutes = sys.argv[7]
task_type = sys.argv[8]
drift_note = sys.argv[9]

summary = "none yet"
changed_target = []
changed_other = []
if previous_result_json.exists():
    try:
        data = json.loads(previous_result_json.read_text(encoding="utf-8"))
    except Exception as exc:
        summary = f"could not parse previous result: {exc}"
    else:
        changed_raw = data.get("changed_files", [])
        for item in changed_raw:
            text = str(item)
            rel = text
            if text.startswith(repo_path):
                rel = text[len(repo_path):].lstrip("/")
            elif text.startswith("./"):
                rel = text[2:]
            if rel == game_path or rel.startswith(game_path.rstrip("/") + "/"):
                changed_target.append(rel)
            else:
                changed_other.append(rel)
        status = data.get("test_result") or data.get("status") or data.get("mode") or "unknown"
        impl = data.get("implementation_summary") or data.get("summary") or "no implementation summary"
        summary = f"status={status}; target_changed={len(changed_target)}; other_changed={len(changed_other)}; summary={impl}"
        if changed_other:
            summary += f"; other_files={', '.join(changed_other[:5])}"

print(f"""Run a long-task browser mini-game session for about {duration_minutes} minutes.
Follow docs/design/long-task-game-execution.md.
Do not ask for step-by-step approval.
Stay autonomous.
Work only on {game_path} inside this repository.
Do not touch sample_app or any unrelated files.
Keep the game playable from file:// without external dependencies.
Improve the game in visible, user-facing layers.
Continue from the previous iteration instead of restarting the design.
Use task type {task_type} and keep the scope fixed on the game artifact.

Current session state:
- iteration: {iteration}
- remaining budget: {remaining_seconds}s
- previous iteration summary: {summary}
- drift warning: {drift_note}

Success criteria:
- produce a visibly improved standalone browser game under {game_path}
- keep the game playable from file:// without external dependencies
- add or strengthen a visible progression loop, restart flow, and results flow
- verify the main JavaScript file locally before finishing

Return only the final artifact path, key changes, and verification results.
""")
PY
}

render_iteration_block() {
  local iteration="$1"
  local result_json="$2"
  local repo_root="$3"
  local target_path="$4"
  python3 - "$iteration" "$result_json" "$repo_root" "$target_path" <<'PY'
from pathlib import Path
import json
import sys

iteration = sys.argv[1]
result_path = Path(sys.argv[2])
repo_root = Path(sys.argv[3]).resolve()
target_path = sys.argv[4].strip("/")

status = "unknown"
test_result = "unknown"
summary = "no summary available"
target_files: list[str] = []
other_files: list[str] = []
drift = "no"
provider = "unknown"

if result_path.exists():
    try:
        data = json.loads(result_path.read_text(encoding="utf-8"))
    except Exception as exc:
        summary = f"could not parse iteration result: {exc}"
    else:
        status = str(data.get("status") or data.get("mode") or "unknown")
        test_result = str(data.get("test_result") or data.get("verification", {}).get("result") or "unknown")
        summary = str(data.get("implementation_summary") or data.get("summary") or data.get("output") or "no summary available")
        provider = str(data.get("runtime_provider") or data.get("provider") or data.get("provider_info", {}).get("provider") or "unknown")
        changed_raw = data.get("changed_files", [])
        for item in changed_raw:
            text = str(item)
            rel = text
            if text.startswith(str(repo_root)):
                rel = text[len(str(repo_root)):].lstrip("/")
            elif text.startswith("./"):
                rel = text[2:]
            if rel == target_path or rel.startswith(target_path + "/"):
                target_files.append(rel)
            else:
                other_files.append(rel)
        drift = "yes" if other_files else "no"

print(f"""### Iteration {iteration} / 第 {iteration} 轮

- result file: {result_path}
- provider or path: {provider}
- status: {status}
- test result: {test_result}
- target files changed: {len(target_files)}
- other files changed: {len(other_files)}
- drift observed: {drift}
- summary: {summary}
""")
if target_files:
    print("- target file list:")
    for item in target_files[:10]:
        print(f"  - {item}")
if other_files:
    print("- other file list:")
    for item in other_files[:10]:
        print(f"  - {item}")
PY
}

mkdir -p "$LOG_DIR" "$SESSION_DIR"
START_ISO="$(utc_now_iso)"
START_EPOCH="$(utc_now_epoch)"
PLANNED_END_ISO="$(python3 - "$START_EPOCH" "$DURATION_SECONDS" <<'PY'
from datetime import datetime, timedelta, timezone
import sys

start_epoch = int(sys.argv[1])
duration_seconds = int(sys.argv[2])
start = datetime.fromtimestamp(start_epoch, tz=timezone.utc)
print((start + timedelta(seconds=duration_seconds)).isoformat().replace("+00:00", "Z"))
PY
)"
DEADLINE_EPOCH=$((START_EPOCH + DURATION_SECONDS))

echo "==> Initializing long-task game session log"
INITIAL_RESULT_JSON="$SESSION_DIR/iteration-0.json"
INITIAL_BLOCK=""
INITIAL_BLOCK_PATH="$SESSION_DIR/session-blocks.initial.md"
printf '%s' "$INITIAL_BLOCK" > "$INITIAL_BLOCK_PATH"
write_session_log "PENDING" "PENDING" "pending" "pending" "session started; provider run not yet completed" "0" "no" "$INITIAL_BLOCK_PATH"

ITERATION_COUNT=0
SESSION_BLOCKS=""
LAST_RESULT_JSON="$INITIAL_RESULT_JSON"
DRIFT_OBSERVED="no"
LAST_PROVIDER_PATH="$PROVIDER"

echo "==> Launching autonomous long-task run"
while :; do
  NOW_EPOCH="$(utc_now_epoch)"
  REMAINING_SECONDS=$((DEADLINE_EPOCH - NOW_EPOCH))
  if (( REMAINING_SECONDS <= 0 )); then
    break
  fi

  ITERATION_COUNT=$((ITERATION_COUNT + 1))
  ITERATION_BUDGET=$ITERATION_BUDGET_SECONDS
  if (( ITERATION_BUDGET > REMAINING_SECONDS )); then
    ITERATION_BUDGET="$REMAINING_SECONDS"
  fi

  ITERATION_RESULT_JSON="$SESSION_DIR/iteration-$ITERATION_COUNT.json"
  PREVIOUS_RESULT_JSON="$LAST_RESULT_JSON"
  if [[ -f "$PREVIOUS_RESULT_JSON" ]]; then
    if [[ -s "$PREVIOUS_RESULT_JSON" ]]; then
      DRIFT_NOTE="previous iteration changed files outside the target only if reported; stay constrained to $GAME_PATH"
    else
      DRIFT_NOTE="no previous iteration result yet"
    fi
  else
    DRIFT_NOTE="no previous iteration result yet"
  fi

  PROMPT="$(build_iteration_prompt "$ITERATION_COUNT" "$REMAINING_SECONDS" "$PREVIOUS_RESULT_JSON" "$DRIFT_NOTE")"

  set +e
  if [[ "$PROVIDER" == "local" ]]; then
    iteration_command=(
      run_with_optional_timeout "$ITERATION_BUDGET"
      python3 -m app.cli.main "$PROMPT"
      --repo "$REPO_PATH"
      --provider "$PROVIDER"
      --auth-source "$AUTH_SOURCE"
      --task-type "$TASK_TYPE"
      --json
    )
  else
    iteration_command=(
      run_with_optional_timeout "$ITERATION_BUDGET"
      python3 -m app.cli.main "$PROMPT"
      --repo "$REPO_PATH"
      --provider "$PROVIDER"
      --auth-source "$AUTH_SOURCE"
      --task-type "$TASK_TYPE"
      --delegate-to-provider
      --auto-approve
      --dangerously-skip-confirmation
      --json
    )
  fi
  run_with_spinner "iteration $ITERATION_COUNT" "$ITERATION_RESULT_JSON" "${iteration_command[@]}"
  RUN_EXIT_CODE=$?
  set -e

  LAST_RESULT_JSON="$ITERATION_RESULT_JSON"
  LAST_PROVIDER_PATH="$PROVIDER"
  ITERATION_BLOCK="$(render_iteration_block "$ITERATION_COUNT" "$ITERATION_RESULT_JSON" "$REPO_PATH" "$GAME_PATH")"
  SESSION_BLOCKS+="${ITERATION_BLOCK}"$'\n'

  DRIFT_THIS_ITERATION="$(python3 - "$ITERATION_RESULT_JSON" "$REPO_PATH" "$GAME_PATH" <<'PY'
from pathlib import Path
import json
import sys

result_path = Path(sys.argv[1])
repo_root = Path(sys.argv[2]).resolve()
target_path = sys.argv[3].strip("/")
drift = "no"
if result_path.exists():
    try:
        data = json.loads(result_path.read_text(encoding="utf-8"))
    except Exception:
        drift = "yes"
    else:
        for item in data.get("changed_files", []):
            text = str(item)
            rel = text
            if text.startswith(str(repo_root)):
                rel = text[len(str(repo_root)):].lstrip("/")
            elif text.startswith("./"):
                rel = text[2:]
            if not (rel == target_path or rel.startswith(target_path + "/")):
                drift = "yes"
                break
print(drift)
PY
)"
  if [[ "$DRIFT_THIS_ITERATION" == "yes" ]]; then
    DRIFT_OBSERVED="yes"
  fi

  if (( RUN_EXIT_CODE != 0 )); then
    if (( REMAINING_SECONDS <= ITERATION_BUDGET )); then
      break
    fi
  fi
done

END_ISO="$(utc_now_iso)"
END_EPOCH="$(utc_now_epoch)"
ELAPSED_SECONDS=$((END_EPOCH - START_EPOCH))
if (( ELAPSED_SECONDS < 0 )); then
  ELAPSED_SECONDS=0
fi
ELAPSED_TEXT="${ELAPSED_SECONDS}s"
if (( ELAPSED_SECONDS >= DURATION_SECONDS )); then
  SUSTAINED_TARGET="yes"
else
  SUSTAINED_TARGET="no"
fi

VERIFICATION_RESULT="skipped"
VERIFY_NOTES="provider run exit code: $RUN_EXIT_CODE; last iteration result: $LAST_RESULT_JSON"
if [[ -f "$TARGET_ABS_PATH/game.js" ]]; then
  set +e
  bash -lc "$VERIFY_COMMAND" >/dev/null 2>&1
  VERIFY_EXIT_CODE=$?
  set -e
  if [[ "$VERIFY_EXIT_CODE" -eq 0 ]]; then
    VERIFICATION_RESULT="passed"
  else
    VERIFICATION_RESULT="failed (exit $VERIFY_EXIT_CODE)"
  fi
  VERIFY_NOTES="$VERIFY_NOTES; verify command: $VERIFY_COMMAND"
fi

SESSION_BLOCKS_PATH="$SESSION_DIR/session-blocks.final.md"
printf '%s' "$SESSION_BLOCKS" > "$SESSION_BLOCKS_PATH"
write_session_log "$END_ISO" "$ELAPSED_TEXT" "$SUSTAINED_TARGET" "$VERIFICATION_RESULT" "$VERIFY_NOTES" "$ITERATION_COUNT" "$DRIFT_OBSERVED" "$SESSION_BLOCKS_PATH"
write_summary_json "$END_ISO" "$ELAPSED_SECONDS" "$SUSTAINED_TARGET" "$VERIFICATION_RESULT" "$ITERATION_COUNT" "$DRIFT_OBSERVED" "$LAST_RESULT_JSON" "$LAST_PROVIDER_PATH"

echo "==> Session log written: $LOG_PATH"
echo "==> Run result JSON: $RESULT_JSON_PATH"
echo "==> Verification: $VERIFICATION_RESULT"
if [[ "$KEEP_ARTIFACTS" == "1" || "$KEEP_ARTIFACTS" == "true" || "$KEEP_ARTIFACTS" == "yes" || "$KEEP_ARTIFACTS" == "on" ]]; then
  echo "==> Artifacts retained"
fi
