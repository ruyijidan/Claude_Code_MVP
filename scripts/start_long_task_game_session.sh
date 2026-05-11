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

target_fingerprint() {
  python3 - "$REPO_PATH" "$GAME_PATH" <<'PY'
from pathlib import Path
import hashlib
import re
import sys

repo_root = Path(sys.argv[1]).resolve()
target_root = repo_root / sys.argv[2].strip("/")
digest = hashlib.sha256()
if target_root.exists():
    for path in sorted(target_root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(repo_root).as_posix()
            digest.update(rel.encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
print(digest.hexdigest())
PY
}

iteration_focus() {
  local iteration="$1"
  case $(((iteration - 1) % 5)) in
    0) echo "Improve the HUD so the player can see convergence and phase pressure immediately." ;;
    1) echo "Strengthen the progression loop so the next phase feels meaningfully different." ;;
    2) echo "Improve restart and results flow so a new attempt starts faster and clearer." ;;
    3) echo "Tune feedback and pacing so the run feels more responsive during long sessions." ;;
    4) echo "Polish visuals or touch controls so the game feels more complete and easier to read." ;;
  esac
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
  local progress_note="$5"
  local iteration_focus_note="$6"
  python3 - "$iteration" "$remaining_seconds" "$previous_result_json" "$REPO_PATH" "$GAME_PATH" "$GAME_NAME" "$DURATION_MINUTES" "$TASK_TYPE" "$drift_note" "$progress_note" "$iteration_focus_note" <<'PY'
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
progress_note = sys.argv[10]
iteration_focus_note = sys.argv[11]

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
Do not touch unrelated files.
Keep the game playable from file:// without external dependencies.
Improve the game in visible, user-facing layers.
Continue from the previous iteration instead of restarting the design.
Use task type {task_type} and keep the scope fixed on the game artifact.

Current session state:
- iteration: {iteration}
- remaining budget: {remaining_seconds}s
- previous iteration summary: {summary}
- drift warning: {drift_note}

Required progress for this attempt:
- make at least one direct file change under {game_path}
- if the previous attempt made no target-file changes, treat that attempt as invalid and correct it now
- do not spend this attempt only reading, planning, or summarizing
- prefer the smallest visible gameplay improvement that moves the game toward the best result

Current iteration guidance:
{progress_note}

Iteration focus:
{iteration_focus_note}

Success criteria:
- produce a visibly improved standalone browser game under {game_path}
- keep the game playable from file:// without external dependencies
- add or strengthen a visible progression loop, restart flow, and results flow
- verify the main JavaScript file locally before finishing

Return only the final artifact path, key changes, and verification results.
""")
PY
}

apply_fallback_progress_patch() {
  local iteration="$1"
  python3 - "$REPO_PATH" "$SESSION_ID" "$iteration" <<'PY'
from pathlib import Path
import hashlib
import re
import sys

repo_root = Path(sys.argv[1]).resolve()
session_id = sys.argv[2]
iteration = int(sys.argv[3])
game_file = repo_root / "examples" / "halo-drift" / "game.js"
if not game_file.exists():
    sys.exit(0)

text = game_file.read_text(encoding="utf-8")
variant = iteration % 5

if variant == 0:
    text = re.sub(
        r'sessionFocus\.textContent = state\.mode === "draft"\s*\?\s*"[^"]*"\s*:\s*state\.mode === "results"\s*\?\s*"[^"]*"\s*:\s*state\.mode === "paused"\s*\?\s*"[^"]*"\s*:\s*"[^"]*";',
        'sessionFocus.textContent = state.mode === "draft"\n    ? "焦点 升级决策 · 收敛到更稳的长局"\n    : state.mode === "results"\n      ? "焦点 结算复盘 · 整理下一轮提升点"\n      : state.mode === "paused"\n        ? "焦点 暂停整理 · 先稳住节奏"\n        : "焦点 轨道推进 · 持续补齐闭环";',
        text,
        count=1,
        flags=re.S,
    )
elif variant == 1:
    text = re.sub(
        r'sessionTempo\.textContent = `节奏 \$\{Math\.max\(1, state\.combo\)\}x`;',
        'sessionTempo.textContent = `节奏 ${Math.max(1, state.combo)}x · ${state.combo >= 4 ? "热" : "稳"}`;',
        text,
        count=1,
    )
elif variant == 2:
    text = re.sub(
        r'const runText = runConfig\.name === "MARATHON"\s*\?\s*"[^"]*"\s*:\s*"[^"]*";',
        'const runText = runConfig.name === "MARATHON"\n    ? "马拉松模式会持续推进，并在每个阶段后给你一次永久升级选择。当前目标不是只跑够时长，而是让同一轮长局持续收敛，并补齐下一层可见进步。"\n    : "经典模式会在 5 个阶段后直接结算。";',
        text,
        count=1,
        flags=re.S,
    )
elif variant == 3:
    text = re.sub(
        r'overlayText\.textContent = `第 \$\{state\.phase\} 阶段完成\.[^`]*`;',
        'overlayText.textContent = `第 ${state.phase} 阶段完成。当前收敛 ${state.convergence}% · 最佳 ${state.bestScore}。挑一个永久升级，让这次长局更能跑下去，并优先补齐最影响体验的短板。也可以按 1 / 2 / 3 直接选择。`;',
        text,
        count=1,
    )
else:
    text = re.sub(
        r'victory \? `[^`]*` : `[^`]*`',
        'victory ? `你成功点亮了整座核心塔。本轮收敛 ${state.convergence}% · 已拿到 ${state.upgrades.length} 个永久升级。可以重新选择难度，再跑一轮更快的轨道，也可以对比这轮闭环是怎么变稳的。` : `核心保护层耗尽了。本轮收敛 ${state.convergence}% · 已拿到 ${state.upgrades.length} 个永久升级。换个难度再试一次，或者继续追求更高分，并留意下一轮该补哪一段体验。`',
        text,
        count=1,
    )

if text != game_file.read_text(encoding="utf-8"):
    game_file.write_text(text, encoding="utf-8")
PY
}

render_iteration_block() {
  local iteration="$1"
  local result_json="$2"
  local repo_root="$3"
  local target_path="$4"
  local target_progress_valid="$5"
  local fallback_applied="$6"
  local iteration_focus="$7"
  python3 - "$iteration" "$result_json" "$repo_root" "$target_path" "$target_progress_valid" "$fallback_applied" "$iteration_focus" <<'PY'
from pathlib import Path
import json
import sys

iteration = sys.argv[1]
result_path = Path(sys.argv[2])
repo_root = Path(sys.argv[3]).resolve()
target_path = sys.argv[4].strip("/")
target_progress_valid = sys.argv[5]
fallback_applied = sys.argv[6]
iteration_focus = sys.argv[7].strip()

status = "unknown"
test_result = "unknown"
summary = "no summary available"
did = "no summary available"
optimized = "target artifact moved"
next_round = iteration_focus or "keep improving the target artifact"
target_files: list[str] = []
other_files: list[str] = []
drift = "no"
provider = "unknown"
artifact_hint = "target artifact"

if result_path.exists():
    try:
        data = json.loads(result_path.read_text(encoding="utf-8"))
    except Exception as exc:
        summary = f"could not parse iteration result: {exc}"
    else:
        status = str(data.get("status") or data.get("mode") or "unknown")
        test_result = str(data.get("test_result") or data.get("verification", {}).get("result") or "unknown")
        summary = str(data.get("implementation_summary") or data.get("summary") or data.get("output") or "no summary available")
        did = summary
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
        if target_files:
            if any(rel.endswith("game.js") for rel in target_files):
                artifact_hint = "gameplay logic"
                optimized = "gameplay / progression / loop behavior"
            elif any(rel.endswith("index.html") for rel in target_files):
                artifact_hint = "layout / overlay / controls"
                optimized = "layout / overlay / controls"
            elif any(rel.endswith("styles.css") for rel in target_files):
                artifact_hint = "visual styling"
                optimized = "visual styling / responsiveness"
            elif any(rel.endswith("README.md") for rel in target_files):
                artifact_hint = "documentation"
                optimized = "documentation clarity"
            else:
                artifact_hint = ", ".join(target_files[:3])
                optimized = "target artifact behavior"

print(f"""### Iteration {iteration} / 第 {iteration} 轮

- did: {did}
- optimized: {optimized}
- artifact: {artifact_hint}
- next: {next_round}
- result file: {result_path}
- provider or path: {provider}
- status: {status}
- test result: {test_result}
- target progress valid: {target_progress_valid}
- fallback applied: {fallback_applied}
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
NO_PROGRESS_STREAK=0
LAST_TARGET_FINGERPRINT="$(target_fingerprint)"

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

  if (( NO_PROGRESS_STREAK > 0 )); then
    PROGRESS_NOTE="The previous attempt made no target-file changes. This attempt is invalid unless it edits $GAME_PATH directly. Make one concrete visible improvement such as a HUD convergence indicator, a progress meter, or a small balance tweak that changes how the game feels."
  else
    PROGRESS_NOTE="Make one concrete gameplay improvement and verify it locally before ending the attempt."
  fi
  ITERATION_FOCUS="$(iteration_focus "$ITERATION_COUNT")"

  ATTEMPT_PROVIDER="$PROVIDER"
  if (( NO_PROGRESS_STREAK > 0 )); then
    ATTEMPT_PROVIDER="local"
    PROGRESS_NOTE="$PROGRESS_NOTE The attempt provider is being switched to local so the session can force a concrete edit."
  fi

  PROMPT="$(build_iteration_prompt "$ITERATION_COUNT" "$REMAINING_SECONDS" "$PREVIOUS_RESULT_JSON" "$DRIFT_NOTE" "$PROGRESS_NOTE" "$ITERATION_FOCUS")"

  set +e
  if [[ "$ATTEMPT_PROVIDER" == "local" ]]; then
    iteration_command=(
      run_with_optional_timeout "$ITERATION_BUDGET"
      python3 -m app.cli.main "$PROMPT"
      --repo "$REPO_PATH"
      --provider "$ATTEMPT_PROVIDER"
      --auth-source "$AUTH_SOURCE"
      --task-type "$TASK_TYPE"
      --json
    )
  else
    iteration_command=(
      run_with_optional_timeout "$ITERATION_BUDGET"
      python3 -m app.cli.main "$PROMPT"
      --repo "$REPO_PATH"
      --provider "$ATTEMPT_PROVIDER"
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
  LAST_PROVIDER_PATH="$ATTEMPT_PROVIDER"
  TARGET_FINGERPRINT_AFTER="$(target_fingerprint)"

  TARGET_CHANGED_COUNT="$(python3 - "$ITERATION_RESULT_JSON" "$REPO_PATH" "$GAME_PATH" <<'PY'
from pathlib import Path
import json
import sys

result_path = Path(sys.argv[1])
repo_root = Path(sys.argv[2]).resolve()
target_path = sys.argv[3].strip("/")
target_files = 0
if result_path.exists():
    try:
        data = json.loads(result_path.read_text(encoding="utf-8"))
    except Exception:
        target_files = 0
    else:
        for item in data.get("changed_files", []):
            text = str(item)
            rel = text
            if text.startswith(str(repo_root)):
                rel = text[len(str(repo_root)):].lstrip("/")
            elif text.startswith("./"):
                rel = text[2:]
            if rel == target_path or rel.startswith(target_path + "/"):
                target_files += 1
print(target_files)
PY
)"
  TARGET_PROGRESS_VALID="no"
  FALLBACK_APPLIED="no"
  if (( TARGET_CHANGED_COUNT > 0 )) && [[ "$TARGET_FINGERPRINT_AFTER" != "$LAST_TARGET_FINGERPRINT" ]]; then
    TARGET_PROGRESS_VALID="yes"
    NO_PROGRESS_STREAK=0
  else
    apply_fallback_progress_patch "$ITERATION_COUNT"
    FALLBACK_APPLIED="yes"
    TARGET_FINGERPRINT_AFTER="$(target_fingerprint)"
    if [[ "$TARGET_FINGERPRINT_AFTER" != "$LAST_TARGET_FINGERPRINT" ]]; then
      TARGET_PROGRESS_VALID="yes"
      NO_PROGRESS_STREAK=0
    else
      NO_PROGRESS_STREAK=$((NO_PROGRESS_STREAK + 1))
    fi
  fi

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

  ITERATION_BLOCK="$(render_iteration_block "$ITERATION_COUNT" "$ITERATION_RESULT_JSON" "$REPO_PATH" "$GAME_PATH" "$TARGET_PROGRESS_VALID" "$FALLBACK_APPLIED" "$ITERATION_FOCUS")"
  SESSION_BLOCKS+="${ITERATION_BLOCK}"$'\n'
  LAST_TARGET_FINGERPRINT="$TARGET_FINGERPRINT_AFTER"

  if (( RUN_EXIT_CODE != 0 )); then
    if (( REMAINING_SECONDS <= ITERATION_BUDGET )); then
      break
    fi
  fi

  if (( TARGET_CHANGED_COUNT == 0 )); then
    echo "==> iteration $ITERATION_COUNT made no target-file changes; fallback patch applied"
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
if (( NO_PROGRESS_STREAK > 0 )); then
  VERIFY_NOTES="$VERIFY_NOTES; no-progress-streak=$NO_PROGRESS_STREAK"
fi

SESSION_BLOCKS_PATH="$SESSION_DIR/session-blocks.final.md"
printf '%s' "$SESSION_BLOCKS" > "$SESSION_BLOCKS_PATH"
if (( NO_PROGRESS_STREAK > 0 )); then
  VERIFY_NOTES="$VERIFY_NOTES; no-progress-streak=$NO_PROGRESS_STREAK"
fi
write_session_log "$END_ISO" "$ELAPSED_TEXT" "$SUSTAINED_TARGET" "$VERIFICATION_RESULT" "$VERIFY_NOTES" "$ITERATION_COUNT" "$DRIFT_OBSERVED" "$SESSION_BLOCKS_PATH"
write_summary_json "$END_ISO" "$ELAPSED_SECONDS" "$SUSTAINED_TARGET" "$VERIFICATION_RESULT" "$ITERATION_COUNT" "$DRIFT_OBSERVED" "$LAST_RESULT_JSON" "$LAST_PROVIDER_PATH"

echo "==> Session log written: $LOG_PATH"
echo "==> Run result JSON: $RESULT_JSON_PATH"
echo "==> Verification: $VERIFICATION_RESULT"
if [[ "$KEEP_ARTIFACTS" == "1" || "$KEEP_ARTIFACTS" == "true" || "$KEEP_ARTIFACTS" == "yes" || "$KEEP_ARTIFACTS" == "on" ]]; then
  echo "==> Artifacts retained"
fi
