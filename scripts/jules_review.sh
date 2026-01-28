#!/usr/bin/env bash
set -euo pipefail

# Jules Code Review Script for Ralph Loop
# Called by Claude at milestones: (1) tests green first time, (2) before push, (3) before DONE
#
# Usage: ./scripts/jules_review.sh
# Output: JSON to stdout, logs to stderr
# Exit codes: 0 = OK (approved/needs_work/skipped/error), 1 = blocking issues

# Find CURRENT_TASK.md (check multiple locations)
TASK_FILE=""
for f in docs/CURRENT_TASK.md CURRENT_TASK.md; do
  [[ -f "$f" ]] && TASK_FILE="$f" && break
done

REVIEW_DIR=".claude/reviews"
REQUEST_FILE="$REVIEW_DIR/review_request.md"

mkdir -p "$REVIEW_DIR"

# Collect context
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
# Truncate diff to 500 lines to avoid pipefail issues
DIFF="$(git diff --unified=3 HEAD~1 2>/dev/null | head -500 || git diff --unified=3 HEAD | head -500 || true)"

echo "== Jules Review Request ==" >&2
echo "Branch: $BRANCH" >&2

# Build request (avoid pipes inside brace block due to pipefail)
{
  echo "# CODE REVIEW REQUEST"
  echo
  echo "## Task Context"
  if [[ -n "$TASK_FILE" ]]; then
    head -80 "$TASK_FILE"
  else
    echo "(No CURRENT_TASK.md found)"
  fi
  echo
  echo "## Changes (Diff)"
  echo '```diff'
  printf '%s\n' "$DIFF"
  echo '```'
} > "$REQUEST_FILE"

echo "Request saved: $REQUEST_FILE" >&2

# Helper to output JSON and determine exit code
output_and_exit() {
  local json="$1"
  echo "$json"

  # Exit code based on status (requires jq)
  if command -v jq &>/dev/null; then
    local status
    status=$(echo "$json" | jq -r '.status // "unknown"')
    case "$status" in
      blocking) exit 1 ;;
      *) exit 0 ;;
    esac
  fi
  exit 0
}

# Check if Jules CLI is available
if ! command -v jules &>/dev/null; then
  echo "WARNING: jules CLI not found, skipping review" >&2
  output_and_exit '{"status":"skipped","reason":"jules CLI not installed","issues":[],"summary":"Review skipped - install jules CLI"}'
fi

# Check if jules has a review command by looking at help output
if ! jules --help 2>&1 | grep -q "review"; then
  echo "WARNING: jules CLI does not have a review command, skipping review" >&2
  output_and_exit '{"status":"skipped","reason":"jules review command not available","issues":[],"summary":"Review skipped - jules CLI does not have review command"}'
fi

# Jules has review command - run it
echo "Running jules review..." >&2
TEMP_RESPONSE=$(mktemp)
if jules review --input "$REQUEST_FILE" --output "$TEMP_RESPONSE" --format json 2>&2; then
  echo "Review complete" >&2
  if [[ -f "$TEMP_RESPONSE" && -s "$TEMP_RESPONSE" ]]; then
    RESPONSE=$(cat "$TEMP_RESPONSE")
    rm -f "$TEMP_RESPONSE"
    output_and_exit "$RESPONSE"
  else
    rm -f "$TEMP_RESPONSE"
    output_and_exit '{"status":"error","reason":"empty response","issues":[],"summary":"Jules returned empty response"}'
  fi
else
  echo "WARNING: jules review command failed" >&2
  rm -f "$TEMP_RESPONSE"
  output_and_exit '{"status":"error","reason":"jules command failed","issues":[],"summary":"Jules review failed"}'
fi
