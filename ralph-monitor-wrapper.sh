#!/bin/bash
# ════════════════════════════════════════════════════════════════════════════════
# Ralph Loop Monitor Wrapper
# ════════════════════════════════════════════════════════════════════════════════
#
# Wraps Claude Code to provide real-time monitoring of the Ralph Loop workflow.
# Detects state from stdout patterns and sends updates to the monitor dashboard.
#
# Usage:
#   ./ralph-monitor-wrapper.sh claude "Start task GE-123"
#   ./ralph-monitor-wrapper.sh --task "GE-123" claude
#
# Environment:
#   MONITOR_URL - Monitor API base URL (default: http://localhost:5000)
#
# ════════════════════════════════════════════════════════════════════════════════

set -euo pipefail

MONITOR_URL="${MONITOR_URL:-http://localhost:5000}"
MONITOR_API="$MONITOR_URL/api/monitor"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ════════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ════════════════════════════════════════════════════════════════════════════════

notify() {
    local endpoint="$1"
    local data="$2"
    # Fire-and-forget: send in background, ignore errors
    curl -s -X POST "$MONITOR_API/$endpoint" \
        -H "Content-Type: application/json" \
        -d "$data" \
        --max-time 2 \
        >/dev/null 2>&1 &
}

notify_event() {
    local type="$1"
    local message="$2"
    local source="${3:-wrapper}"
    notify "event" "{\"event_type\": \"$type\", \"message\": \"$message\", \"source\": \"$source\"}"
}

notify_node() {
    local node="$1"
    local message="${2:-}"
    notify "node-state" "{\"node\": \"$node\", \"state\": \"active\", \"message\": \"$message\"}"
}

notify_task_start() {
    local task_id="$1"
    local title="${2:-}"
    notify "task" "{\"action\": \"start\", \"task_id\": \"$task_id\", \"title\": \"$title\"}"
}

notify_task_update() {
    local step="$1"
    local desc="${2:-}"
    notify "task" "{\"action\": \"update\", \"step\": $step, \"step_desc\": \"$desc\"}"
}

notify_task_complete() {
    notify "task" "{\"action\": \"complete\"}"
}

# ════════════════════════════════════════════════════════════════════════════════
# State Detection from Output
# ════════════════════════════════════════════════════════════════════════════════

detect_and_notify() {
    local last_node=""

    while IFS= read -r line; do
        # Pass through to terminal
        echo "$line"

        # Detect state from output patterns
        case "$line" in
            # Jira/Reading patterns
            *"Reading"*|*"Fetching"*|*"Analyzing"*|*"Searching"*|*"Finding"*)
                if [[ "$last_node" != "jira" ]]; then
                    notify_node "jira" "Analyzing codebase..."
                    last_node="jira"
                fi
                ;;

            # Claude/Writing patterns
            *"Writing"*|*"Creating"*|*"Editing"*|*"Implementing"*|*"Adding"*)
                if [[ "$last_node" != "claude" ]]; then
                    notify_node "claude" "Writing code..."
                    last_node="claude"
                fi
                ;;

            # GitHub patterns
            *"git commit"*|*"Committing"*)
                notify_node "github" "Committing changes..."
                last_node="github"
                ;;
            *"git push"*|*"Pushing"*)
                notify_node "github" "Pushing to remote..."
                last_node="github"
                ;;
            *"gh pr create"*|*"Creating PR"*|*"Pull request"*)
                notify_node "github" "Creating pull request..."
                last_node="github"
                ;;

            # CI/Actions patterns
            *"pytest"*|*"Running tests"*|*"test_"*)
                notify_node "actions" "Running tests..."
                last_node="actions"
                ;;
            *"ruff"*|*"Linting"*|*"lint"*)
                notify_node "actions" "Running linter..."
                last_node="actions"
                ;;
            *"npm test"*|*"npm run"*)
                notify_node "actions" "Running npm..."
                last_node="actions"
                ;;

            # Jules/Review patterns
            *"Review"*|*"Reviewing"*|*"Code review"*)
                notify_node "jules" "Reviewing code..."
                last_node="jules"
                ;;

            # Completion patterns
            *"<promise>DONE</promise>"*)
                notify_event "success" "Task completed!" "wrapper"
                notify_task_complete
                ;;
            *"<promise>BLOCKED</promise>"*)
                notify_event "warning" "Task blocked - needs help" "wrapper"
                ;;
            *"<promise>FAILED</promise>"*)
                notify_event "error" "Task failed" "wrapper"
                ;;

            # Error patterns
            *"Error"*|*"ERROR"*|*"Failed"*|*"FAILED"*)
                notify_event "error" "Error detected" "wrapper"
                ;;

            # Success patterns
            *"passed"*|*"PASSED"*|*"✓"*|*"success"*)
                notify_event "success" "Check passed" "wrapper"
                ;;
        esac
    done
}

# ════════════════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════════════════

main() {
    local task_id=""
    local task_title=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --task|-t)
                task_id="$2"
                shift 2
                ;;
            --title)
                task_title="$2"
                shift 2
                ;;
            --help|-h)
                echo "Ralph Loop Monitor Wrapper"
                echo ""
                echo "Usage: $0 [OPTIONS] COMMAND [ARGS...]"
                echo ""
                echo "Options:"
                echo "  --task, -t ID    Jira task ID (e.g., GE-123)"
                echo "  --title TEXT     Task title"
                echo "  --help, -h       Show this help"
                echo ""
                echo "Environment:"
                echo "  MONITOR_URL      Monitor API URL (default: http://localhost:5000)"
                echo ""
                echo "Examples:"
                echo "  $0 --task GE-123 claude"
                echo "  $0 claude \"Work on task GE-123\""
                exit 0
                ;;
            *)
                break
                ;;
        esac
    done

    if [[ $# -eq 0 ]]; then
        echo -e "${RED}Error: No command specified${NC}" >&2
        echo "Usage: $0 [OPTIONS] COMMAND [ARGS...]" >&2
        exit 1
    fi

    # Extract task ID from command if not provided
    if [[ -z "$task_id" ]]; then
        # Look for Jira-style IDs in the arguments
        for arg in "$@"; do
            if [[ "$arg" =~ ([A-Z]+-[0-9]+) ]]; then
                task_id="${BASH_REMATCH[1]}"
                break
            fi
        done
    fi

    # Notify task start if we have a task ID
    if [[ -n "$task_id" ]]; then
        echo -e "${CYAN}╭────────────────────────────────────────╮${NC}"
        echo -e "${CYAN}│${NC}  Ralph Loop Monitor: ${GREEN}$task_id${NC}"
        echo -e "${CYAN}│${NC}  Dashboard: ${BLUE}$MONITOR_URL/static/monitor.html${NC}"
        echo -e "${CYAN}╰────────────────────────────────────────╯${NC}"
        echo ""

        notify_task_start "$task_id" "$task_title"
        notify_event "info" "Starting task $task_id" "wrapper"
        notify_node "jira" "Fetching task $task_id..."
    else
        echo -e "${YELLOW}Note: No task ID detected. Monitor will track activity without task context.${NC}"
        echo -e "${YELLOW}Use --task ID or include PROJ-123 style ID in command.${NC}"
        echo ""
    fi

    # Run the command with output monitoring
    # Use stdbuf to ensure line-buffered output for real-time detection
    if command -v stdbuf >/dev/null 2>&1; then
        stdbuf -oL -eL "$@" 2>&1 | detect_and_notify
        exit_code="${PIPESTATUS[0]}"
    else
        "$@" 2>&1 | detect_and_notify
        exit_code="${PIPESTATUS[0]}"
    fi

    # Report final status
    if [[ $exit_code -eq 0 ]]; then
        notify_event "success" "Command completed successfully" "wrapper"
    else
        notify_event "error" "Command exited with code $exit_code" "wrapper"
    fi

    exit "$exit_code"
}

main "$@"
