#!/usr/bin/env bash
set -euo pipefail

BRANCH="${1:-}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_BRANCH="$(git -C "$ROOT_DIR" branch --show-current)"

if [[ -z "$BRANCH" ]]; then
  BRANCH="$DEFAULT_BRANCH"
fi

WORKTREE_DIR="/tmp/claude-code-mvp-verify-$(date +%s)"

cleanup() {
  if [[ -d "$WORKTREE_DIR" ]]; then
    git -C "$ROOT_DIR" worktree remove --force "$WORKTREE_DIR" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT

echo "🔧 Creating verification worktree for branch: $BRANCH"
if git -C "$ROOT_DIR" worktree list --porcelain | grep -F "branch refs/heads/$BRANCH" >/dev/null 2>&1; then
  echo "ℹ️ Branch $BRANCH is already checked out; creating a detached verification worktree"
  git -C "$ROOT_DIR" worktree add --detach "$WORKTREE_DIR" "$BRANCH" >/dev/null
else
  git -C "$ROOT_DIR" worktree add "$WORKTREE_DIR" "$BRANCH" >/dev/null
fi

echo "🔄 Syncing current workspace into verification worktree"
rsync -rlt --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude 'logs' \
  "$ROOT_DIR"/ "$WORKTREE_DIR"/ >/dev/null

cd "$WORKTREE_DIR"

echo "📦 Installing project"
python3 -m pip install . >/tmp/claude_code_mvp_verify_pip.log 2>&1 || {
  echo "❌ Install failed"
  cat /tmp/claude_code_mvp_verify_pip.log
  exit 1
}

echo "🏗 Running architecture checks"
python3 scripts/check_architecture.py || {
  echo "❌ Architecture boundary checks failed"
  exit 1
}

echo "🧪 Running unit tests"
python3 -m unittest discover -s tests || {
  echo "❌ Unit tests failed"
  exit 1
}

echo "✅ Verification passed for branch: $BRANCH"
