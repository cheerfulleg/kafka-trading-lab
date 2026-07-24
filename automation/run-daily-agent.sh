#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$PROJECT_DIR/.agent-logs"
LOCK_DIR="$PROJECT_DIR/.agent-run.lock"
DEFAULT_BRANCH="${DEFAULT_BRANCH:-main}"
RUN_ID="$(date '+%Y%m%d-%H%M%S')"
BRANCH="codex/daily-$RUN_ID"
LOG_FILE="$LOG_DIR/$RUN_ID.log"
SUMMARY_FILE="$LOG_DIR/$RUN_ID-summary.md"

mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "Another daily agent run is active; exiting."
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

for command in codex git gh; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Missing required command: $command"
    exit 1
  fi
done

cd "$PROJECT_DIR"

codex login status
gh auth status

if [ -n "$(git status --porcelain)" ]; then
  echo "Working tree is not clean. Commit or stash your changes before the scheduled run."
  exit 1
fi

git fetch origin

if gh pr list --state open --json headRefName \
  --jq '.[].headRefName' | grep -q '^codex/daily-'; then
  echo "An earlier daily-agent PR is still open; skipping this run."
  exit 0
fi

git switch "$DEFAULT_BRANCH"
git pull --ff-only origin "$DEFAULT_BRANCH"
git switch -c "$BRANCH"

codex exec \
  --ephemeral \
  --sandbox workspace-write \
  --ask-for-approval never \
  --output-last-message "$SUMMARY_FILE" \
  - < automation/daily-engineer.md

# The agent is never allowed to rewrite its own instructions or guardrails.
git diff --exit-code -- .github automation AGENTS.md

if [ -z "$(git status --porcelain)" ]; then
  echo "Codex produced no useful change; no commit or PR created."
  git switch "$DEFAULT_BRANCH"
  git branch -D "$BRANCH"
  exit 0
fi

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src
.venv/bin/pytest

git add --all
git commit -m "Codex: implement daily backlog item"
git push --set-upstream origin "$BRANCH"

gh pr create \
  --base "$DEFAULT_BRANCH" \
  --head "$BRANCH" \
  --title "Codex: daily Kafka lab improvement" \
  --body-file "$SUMMARY_FILE"

git switch "$DEFAULT_BRANCH"
echo "Daily agent PR created successfully."
