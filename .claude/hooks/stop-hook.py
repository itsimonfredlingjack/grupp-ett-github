#!/usr/bin/env python3
"""
Ralph Loop Stop-Hook

This hook prevents the agent from exiting until:
1. The completion_promise string is found in the transcript
2. All tests pass (verified by promise format)
3. Max iterations haven't been exceeded

Exit codes:
- 0: Allow exit (promise found, criteria met)
- 2: Block exit (continue working)

The hook reads JSON from stdin and writes feedback to stderr.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Flag file that indicates we're in an active Ralph loop
# Only /start-task creates this file, utility commands don't
LOOP_FLAG = Path.cwd() / ".claude" / ".ralph_loop_active"

# CRITICAL: If not in active Ralph loop, allow exit immediately
# This prevents utility commands (/preflight, /finish-task) from being blocked
if not LOOP_FLAG.exists():
    sys.exit(0)  # Allow exit, no enforcement


def load_config():
    """Load Ralph Loop configuration with profile support."""
    config_paths = [
        Path(__file__).parent.parent / "ralph-config.json",
        Path.cwd() / ".claude" / "ralph-config.json",
        Path.cwd() / "ralph-config.json",
    ]

    for config_path in config_paths:
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)

            # Check if this is a profile-based config
            if "profiles" in config:
                active_profile = config.get("active_profile", "template_repo")
                profiles = config.get("profiles", {})
                profile = profiles.get(active_profile, {})
                exit_policy = profile.get("exit_policy", {})
                return exit_policy
            else:
                # Legacy format - return as-is (for backwards compatibility)
                return config.get("exit_policy", config)

    # Default configuration
    return {
        "completion_promise": "<promise>DONE</promise>",
        "max_iterations": 25,
        "scan_length": 5000,
        "requirements": {
            "tests_must_pass": False,
            "lint_must_pass": True
        }
    }


def get_iteration_count():
    """Get current iteration count from state file."""
    state_file = Path.cwd() / ".claude" / "ralph-state.json"
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
            return state.get("iterations", 0)
    return 0


def increment_iteration():
    """Increment and save iteration count."""
    state_file = Path.cwd() / ".claude" / "ralph-state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)

    state = {"iterations": 0, "started_at": datetime.now().isoformat()}
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)

    state["iterations"] = state.get("iterations", 0) + 1
    state["last_check"] = datetime.now().isoformat()

    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

    return state["iterations"]


def check_promise_in_transcript(transcript: str, promise: str) -> bool:
    """Check if completion promise exists in transcript string.

    Args:
        transcript: Transcript content as string
        promise: Promise string to search for

    Returns:
        True if promise found anywhere in transcript
    """
    if not transcript:
        return False
    return promise in transcript


def read_transcript_from_path(transcript_path: str) -> str:
    """Read transcript content from a JSONL file path.

    Args:
        transcript_path: Path to the transcript JSONL file

    Returns:
        Concatenated transcript content, or empty string on error
    """
    try:
        path = Path(transcript_path)
        if not path.exists():
            return ""

        content_parts = []
        with open(path) as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    # Extract text content from various message formats
                    if isinstance(entry, dict):
                        if "content" in entry:
                            content_parts.append(str(entry["content"]))
                        if "message" in entry:
                            content_parts.append(str(entry["message"]))
                except json.JSONDecodeError:
                    continue

        return "\n".join(content_parts)
    except Exception:
        return ""


def check_promise_flag_file(promise: str) -> bool:
    """Check if promise flag file exists and contains the correct promise.

    Flag file location: .claude/.promise_done
    Flag file contains: exact promise string

    Returns:
        True if flag file exists and contains correct promise
    """
    flag_file = Path.cwd() / ".claude" / ".promise_done"

    if not flag_file.exists():
        return False

    try:
        with open(flag_file) as f:
            content = f.read().strip()
        return content == promise
    except Exception:
        return False


def write_promise_flag(promise: str) -> None:
    """Write promise flag file for stop-hook to detect."""
    flag_file = Path.cwd() / ".claude" / ".promise_done"
    flag_file.parent.mkdir(parents=True, exist_ok=True)

    with open(flag_file, 'w') as f:
        f.write(promise)


def build_continue_message(reason: str, suggestions: list) -> dict:
    """Build the JSON response for continuing work."""
    return {
        "action": "continue",
        "reason": reason,
        "suggestions": suggestions,
        "timestamp": datetime.now().isoformat()
    }


def main():
    """Main hook logic."""
    # Debug: Log that hook was called
    debug_file = Path.cwd() / ".claude" / "stop-hook-debug.log"
    debug_file.parent.mkdir(parents=True, exist_ok=True)

    with open(debug_file, "a") as f:
        f.write(f"\n--- Hook called at {datetime.now().isoformat()} ---\n")

    try:
        # Read input from stdin
        input_data = sys.stdin.read()

        # Debug: Log input
        with open(debug_file, "a") as f:
            f.write(f"Input length: {len(input_data)}\n")
            f.write(f"Input preview: {input_data[:500]}...\n")

        if not input_data.strip():
            # No input, allow exit
            sys.exit(0)

        try:
            hook_input = json.loads(input_data)
        except json.JSONDecodeError:
            # Invalid JSON, allow exit (fail open)
            sys.exit(0)

        # Load configuration
        config = load_config()

        # Get values from config
        completion_promise = config.get("completion_promise", "<promise>DONE</promise>")
        max_iterations = config.get("max_iterations", 25)

        # Increment iteration counter
        current_iteration = increment_iteration()

        # Check 1: Max iterations exceeded - force exit
        if current_iteration >= max_iterations:
            with open(debug_file, "a") as f:
                f.write("Decision: ALLOW EXIT - max iterations reached\n")
            response = build_continue_message(
                f"Max iterations ({max_iterations}) reached. Forcing exit.",
                ["Review the task manually", "Check for infinite loops in logic"]
            )
            json.dump(response, sys.stderr)
            sys.exit(0)

        # ===== HYBRID POLICY =====
        # Check 2: Flag file (PRIMARY - source of truth)
        if check_promise_flag_file(completion_promise):
            with open(debug_file, "a") as f:
                f.write("Decision: ALLOW EXIT - promise flag file found (primary)\n")
            sys.exit(0)

        # Check 3: Transcript content (SECONDARY - fallback/diagnostics)
        # Try direct transcript string first
        transcript = hook_input.get("transcript", "")
        if check_promise_in_transcript(transcript, completion_promise):
            with open(debug_file, "a") as f:
                f.write("Decision: ALLOW EXIT - promise in transcript string\n")
            sys.exit(0)

        # Try reading from transcript_path if provided
        transcript_path = hook_input.get("transcript_path", "")
        if transcript_path:
            transcript_content = read_transcript_from_path(transcript_path)
            if check_promise_in_transcript(transcript_content, completion_promise):
                with open(debug_file, "a") as f:
                    f.write("Decision: ALLOW EXIT - promise in transcript file\n")
                sys.exit(0)

        # Promise not found - block exit and provide guidance
        suggestions = [
            "Read CURRENT_TASK.md to review acceptance criteria",
            "Run the test suite and verify all tests pass",
            "Check for linting errors with the appropriate linter",
            f"When all criteria are met, output: {completion_promise}"
        ]

        # Add iteration info
        reason = (
            f"Completion criteria not met "
            f"(iteration {current_iteration}/{max_iterations})"
        )

        response = build_continue_message(reason, suggestions)
        json.dump(response, sys.stderr)

        # Debug: Log blocking decision
        with open(debug_file, "a") as f:
            f.write("Decision: BLOCK EXIT - promise not found\n")
            f.write(f"Iteration: {current_iteration}/{max_iterations}\n")

        # Exit 2 blocks the agent from exiting
        sys.exit(2)

    except Exception as e:
        # On any error, fail open (allow exit) to prevent stuck state
        error_response = {
            "error": str(e),
            "action": "allow_exit_on_error"
        }
        json.dump(error_response, sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
