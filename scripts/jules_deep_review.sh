#!/usr/bin/env bash
set -euo pipefail

# Jules Deep Review Script
# Starts an async Jules review session and optionally waits for results
#
# Usage:
#   ./scripts/jules_deep_review.sh           # Start review, don't wait
#   ./scripts/jules_deep_review.sh --wait    # Start and poll for results (max 10 min)
#   ./scripts/jules_deep_review.sh --status  # Check existing session status
#
# Output: Session info to stdout, logs to stderr

REVIEW_DIR=".claude/reviews"
REQUEST_FILE="$REVIEW_DIR/jules_request.md"
RESPONSE_FILE="$REVIEW_DIR/jules_response.md"
SESSION_FILE="$REVIEW_DIR/jules_session_id"

mkdir -p "$REVIEW_DIR"

# Parse arguments
WAIT_FOR_RESULT=false
CHECK_STATUS=false

for arg in "$@"; do
  case $arg in
    --wait) WAIT_FOR_RESULT=true ;;
    --status) CHECK_STATUS=true ;;
  esac
done

# Function: Check if Jules is available and logged in
check_jules() {
  if ! command -v jules &>/dev/null; then
    echo "ERROR: jules CLI not installed" >&2
    echo "Install: https://github.com/google-labs-code/jules-cli" >&2
    exit 1
  fi

  # Quick check if logged in (list sessions)
  if ! jules remote list --session &>/dev/null; then
    echo "ERROR: Not logged in to Jules" >&2
    echo "Run: jules login" >&2
    exit 1
  fi
}

# Function: Check status of existing session
check_status() {
  if [[ ! -f "$SESSION_FILE" ]]; then
    echo "No active session found" >&2
    echo "Start a new review with: ./scripts/jules_deep_review.sh" >&2
    exit 1
  fi

  SESSION_ID=$(cat "$SESSION_FILE")
  echo "Session ID: $SESSION_ID" >&2
  echo "---" >&2
  jules remote list --session 2>&1 | grep -A2 "$SESSION_ID" || echo "Session not found in list"
}

# Function: Build review prompt
build_prompt() {
  local branch diff task_content

  branch=$(git rev-parse --abbrev-ref HEAD)
  diff=$(git diff main...HEAD 2>/dev/null | head -3000 || git diff HEAD~5...HEAD | head -3000 || echo "No diff available")

  # Find task file
  task_content="(No task file found)"
  for f in docs/CURRENT_TASK.md CURRENT_TASK.md; do
    if [[ -f "$f" ]]; then
      task_content=$(head -50 "$f")
      break
    fi
  done

  cat << EOF
Review the following code changes. Provide structured feedback.

## Review Criteria

### Security (CRITICAL)
- OWASP Top 10 vulnerabilities
- Input validation issues
- Authentication/authorization flaws
- Secrets or credentials exposure
- Injection vulnerabilities (SQL, XSS, command)

### Architecture (HIGH)
- Design pattern violations
- SOLID principle adherence
- Separation of concerns
- Inappropriate coupling

### Performance (MEDIUM)
- N+1 query patterns
- Memory leaks or resource issues
- Inefficient algorithms
- Missing caching opportunities

### Code Quality (LOW)
- Code smells and anti-patterns
- Naming conventions
- Error handling gaps
- Missing edge cases

---

## Branch: $branch

## Task Context
$task_content

## Changes (Diff)
\`\`\`diff
$diff
\`\`\`

---

## Output Format

Respond with structured JSON:
\`\`\`json
{
  "summary": "One-line overall assessment",
  "critical": [
    {"file": "path", "line": 123, "issue": "description", "fix": "suggestion"}
  ],
  "warnings": [
    {"file": "path", "line": 456, "issue": "description", "fix": "suggestion"}
  ],
  "suggestions": [
    {"file": "path", "issue": "description", "fix": "suggestion"}
  ],
  "approved": true/false
}
\`\`\`

If no issues found, return empty arrays and approved: true.
EOF
}

# Function: Start Jules session
start_session() {
  echo "Building review prompt..." >&2
  build_prompt > "$REQUEST_FILE"
  echo "Prompt saved: $REQUEST_FILE" >&2

  echo "Starting Jules session..." >&2

  # Start session and capture output
  SESSION_OUTPUT=$(cat "$REQUEST_FILE" | jules new 2>&1) || true
  echo "$SESSION_OUTPUT" >&2

  # Try to extract session ID
  SESSION_ID=$(echo "$SESSION_OUTPUT" | grep -oE 'session[^0-9]*([0-9]{6,})' | grep -oE '[0-9]+' | head -1 || true)

  if [[ -z "$SESSION_ID" ]]; then
    # Fallback: get latest session from list
    sleep 2
    SESSION_ID=$(jules remote list --session 2>&1 | grep -oE '[0-9]{6,}' | head -1 || true)
  fi

  if [[ -n "$SESSION_ID" ]]; then
    echo "$SESSION_ID" > "$SESSION_FILE"
    echo "Session ID: $SESSION_ID" >&2
    echo "$SESSION_ID"
  else
    echo "WARNING: Could not extract session ID" >&2
    echo "Check manually: jules remote list --session" >&2
  fi
}

# Function: Wait for results with polling
wait_for_results() {
  local session_id="$1"
  local timeout=600  # 10 minutes
  local interval=30
  local elapsed=0

  echo "Waiting for Jules to complete (max ${timeout}s)..." >&2

  while [[ $elapsed -lt $timeout ]]; do
    # Check if session is complete
    STATUS=$(jules remote list --session 2>&1 || true)

    if echo "$STATUS" | grep -qiE "(completed|done|finished|ready)"; then
      echo "Review complete!" >&2

      # Pull results
      jules remote pull --session "$session_id" > "$RESPONSE_FILE" 2>&1 || true

      if [[ -s "$RESPONSE_FILE" ]]; then
        echo "Results saved: $RESPONSE_FILE" >&2
        cat "$RESPONSE_FILE"
        return 0
      fi
    fi

    echo "Waiting... (${elapsed}/${timeout}s)" >&2
    sleep $interval
    elapsed=$((elapsed + interval))
  done

  echo "TIMEOUT: Review did not complete in ${timeout}s" >&2
  echo "Check status manually: jules remote list --session" >&2
  echo "Pull when ready: jules remote pull --session $session_id" >&2
  return 1
}

# Main
main() {
  check_jules

  if [[ "$CHECK_STATUS" == "true" ]]; then
    check_status
    exit 0
  fi

  SESSION_ID=$(start_session)

  if [[ "$WAIT_FOR_RESULT" == "true" && -n "$SESSION_ID" ]]; then
    wait_for_results "$SESSION_ID"
  else
    echo "" >&2
    echo "Review started. To check status:" >&2
    echo "  ./scripts/jules_deep_review.sh --status" >&2
    echo "  jules remote list --session" >&2
    echo "" >&2
    echo "To get results when ready:" >&2
    echo "  jules remote pull --session $SESSION_ID" >&2
  fi
}

main "$@"
