#!/usr/bin/env python3
"""
Ralph Loop Stop-Hook

Goal: prevent the agent from exiting until completion is verifiable.

Enforcement rules:
- When on a Jira-style task branch (e.g. feature/GE-123-...), the hook enforces even if the agent deletes the loop-flag.
- When on main/master, the hook does not enforce (utility commands should not be blocked).
- Outside a git repo (e.g. tests using tmp dirs), enforcement requires the loop flag file.

Exit codes:
- 0: allow exit
- 2: block exit (continue working)
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_PROMISE = "<promise>DONE</promise>"
JIRA_KEY_RE = re.compile(r"[A-Z]+-[0-9]+")

LOOP_FLAG = Path.cwd() / ".claude" / ".ralph_loop_active"
STATE_FILE = Path.cwd() / ".claude" / "ralph-state.json"
PROMISE_FLAG_FILE = Path.cwd() / ".claude" / ".promise_done"
DEBUG_LOG = Path.cwd() / ".claude" / "stop-hook-debug.log"


def _debug(msg: str) -> None:
    if os.environ.get("RALPH_STOP_HOOK_DEBUG") != "1":
        return
    DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(DEBUG_LOG, "a") as f:
        f.write(msg.rstrip() + "\n")


def load_config() -> tuple[dict[str, Any], bool]:
    """Load exit policy config. Returns (policy, has_explicit_config)."""
    config_paths = [
        Path(__file__).parent.parent / "ralph-config.json",
        Path.cwd() / ".claude" / "ralph-config.json",
        Path.cwd() / "ralph-config.json",
    ]

    for config_path in config_paths:
        if not config_path.exists():
            continue

        with open(config_path) as f:
            config = json.load(f)

        if "profiles" in config:
            active_profile = config.get("active_profile", "template_repo")
            profile = (config.get("profiles") or {}).get(active_profile, {}) or {}
            return (profile.get("exit_policy") or {}), True

        # Legacy / flat format
        return (config.get("exit_policy") or config), True

    # Default is permissive so temp-dir tests and utility contexts don't get stuck.
    return (
        {
            "completion_promise": DEFAULT_PROMISE,
            "max_iterations": 25,
            "scan_length": 5000,
            "requirements": {"tests_must_pass": False, "lint_must_pass": False},
        },
        False,
    )


def is_git_repo() -> bool:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except Exception:
        return False


def get_git_branch() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except Exception:
        return None


def should_enforce_exit_policy(hook_input: dict[str, Any]) -> bool:
    """Return True if enforcement should be active."""
    # Strong signal that we're inside a loop: the hook input includes a completion promise.
    if hook_input.get("completion_promise"):
        return True

    if LOOP_FLAG.exists():
        return True

    if not is_git_repo():
        return False

    branch = get_git_branch() or ""
    if branch in {"main", "master"}:
        return False

    # Enforce on branches that look like Jira task branches.
    return bool(JIRA_KEY_RE.search(branch))


def get_transcript_text(hook_input: dict[str, Any], scan_length: int) -> str:
    """Extract transcript content (prefers transcript_path tail for performance)."""
    transcript = hook_input.get("transcript")
    if isinstance(transcript, str) and transcript:
        return transcript

    transcript_path = hook_input.get("transcript_path") or hook_input.get("transcriptPath")
    if not transcript_path:
        return ""

    try:
        path = Path(transcript_path)
        if not path.exists() or not path.is_file():
            return ""

        with open(path, "rb") as f:
            if scan_length and scan_length > 0:
                f.seek(0, 2)
                size = f.tell()
                f.seek(max(size - scan_length, 0))
            data = f.read()

        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def run_cmd(cmd: list[str], timeout_s: int) -> tuple[int, str]:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
    )
    out = ((result.stdout or "") + (result.stderr or "")).strip()
    if len(out) > 1500:
        out = out[:1500] + "\n...(truncated)"
    return result.returncode, out


def resolve_tools() -> dict[str, list[str]]:
    """Resolve pytest/ruff commands; prefer ./venv when present."""
    venv_bin = Path.cwd() / "venv" / "bin"

    python = "python3"
    if (venv_bin / "python").exists():
        python = str(venv_bin / "python")
    elif (venv_bin / "python3").exists():
        python = str(venv_bin / "python3")

    pytest_cmd = [python, "-m", "pytest"]
    if (venv_bin / "pytest").exists():
        pytest_cmd = [str(venv_bin / "pytest")]

    ruff_cmd = ["ruff"]
    if (venv_bin / "ruff").exists():
        ruff_cmd = [str(venv_bin / "ruff")]

    return {"pytest": pytest_cmd, "ruff": ruff_cmd}


def increment_iteration() -> int:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    state: dict[str, Any] = {"iterations": 0, "started_at": datetime.now().isoformat()}
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            state = json.load(f)

    state["iterations"] = int(state.get("iterations", 0)) + 1
    state["last_check"] = datetime.now().isoformat()

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    return int(state["iterations"])


def check_promise_flag_file(promise: str) -> bool:
    if not PROMISE_FLAG_FILE.exists():
        return False
    try:
        return PROMISE_FLAG_FILE.read_text().strip() == promise
    except Exception:
        return False


def write_promise_flag(promise: str) -> None:
    PROMISE_FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROMISE_FLAG_FILE.write_text(promise)


def build_continue_message(reason: str, suggestions: list[str]) -> dict[str, Any]:
    return {
        "decision": "block",
        "action": "continue",
        "reason": reason,
        "suggestions": suggestions,
        "timestamp": datetime.now().isoformat(),
    }


def main() -> None:
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            sys.exit(0)

        try:
            hook_input = json.loads(input_data)
        except json.JSONDecodeError:
            sys.exit(0)

        if not should_enforce_exit_policy(hook_input):
            sys.exit(0)

        config, has_explicit_config = load_config()
        requirements = (config.get("requirements") or {}) if isinstance(config, dict) else {}

        completion_promise = (
            hook_input.get("completion_promise")
            or config.get("completion_promise")
            or DEFAULT_PROMISE
        )
        max_iterations = int(config.get("max_iterations", 25))
        scan_length = int(config.get("scan_length", 5000))

        current_iteration = increment_iteration()
        _debug(f"{datetime.now().isoformat()} iteration={current_iteration} enforce=true")

        if current_iteration >= max_iterations:
            json.dump(
                {
                    "decision": "allow",
                    "reason": f"Max iterations ({max_iterations}) reached. Forcing exit.",
                    "timestamp": datetime.now().isoformat(),
                },
                sys.stderr,
            )
            sys.exit(0)

        transcript = get_transcript_text(hook_input, scan_length)
        promise_found = isinstance(transcript, str) and completion_promise in transcript
        flag_found = check_promise_flag_file(completion_promise)

        if not (promise_found or flag_found):
            response = build_continue_message(
                f"Completion criteria not met (iteration {current_iteration}/{max_iterations})",
                [
                    "Read CURRENT_TASK.md to review acceptance criteria",
                    "Run: pytest -q",
                    "Run: ruff check .",
                    "Run: ruff format --check .",
                    f"When all criteria are met, output: {completion_promise}",
                ],
            )
            json.dump(response, sys.stderr)
            sys.exit(2)

        # Promise is present -> verify required quality gates before allowing exit.
        tools = resolve_tools()
        enforce_tools = has_explicit_config or is_git_repo()

        failures: list[str] = []
        suggestions: list[str] = []

        tests_required = bool(requirements.get("tests_must_pass"))
        lint_required = bool(requirements.get("lint_must_pass"))

        if tests_required and enforce_tools:
            code, out = run_cmd([*tools["pytest"], "-q"], timeout_s=180)
            if code != 0:
                failures.append("pytest -q failed")
                suggestions.append(f"Fix failing tests:\n{out}")

        if lint_required and enforce_tools:
            code, out = run_cmd([*tools["ruff"], "check", "."], timeout_s=120)
            if code != 0:
                failures.append("ruff check . failed")
                suggestions.append(f"Fix Ruff lint:\n{out}")

            code, out = run_cmd([*tools["ruff"], "format", "--check", "."], timeout_s=120)
            if code != 0:
                failures.append("ruff format --check . failed")
                suggestions.append(f"Run formatter:\n{out}")

        if failures:
            response = build_continue_message(
                f"Completion promise found, but quality gates failed "
                f"(iteration {current_iteration}/{max_iterations}): {', '.join(failures)}",
                suggestions
                or [
                    "Run the required checks locally and fix failures",
                    f"When all criteria are met, output: {completion_promise}",
                ],
            )
            json.dump(response, sys.stderr)
            sys.exit(2)

        write_promise_flag(completion_promise)
        sys.exit(0)
    except Exception as e:
        # Fail open to avoid deadlocks in the CLI.
        json.dump(
            {"decision": "allow", "action": "allow_exit_on_error", "error": str(e)},
            sys.stderr,
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
