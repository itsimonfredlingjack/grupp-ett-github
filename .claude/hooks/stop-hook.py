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
import threading
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_PROMISE = "<promise>DONE</promise>"

# Monitor integration (non-blocking)
MONITOR_URL = os.environ.get("MONITOR_URL", "http://localhost:5000")
MONITOR_TIMEOUT = 2


def _notify_monitor(endpoint: str, payload: dict) -> None:
    """Send notification to monitor (fire-and-forget)."""
    def _send():
        try:
            url = f"{MONITOR_URL}/api/monitor/{endpoint}"
            data = json.dumps(payload).encode("utf-8")
            headers = {"Content-Type": "application/json"}
            req = Request(url, data=data, headers=headers, method="POST")
            with urlopen(req, timeout=MONITOR_TIMEOUT):
                pass
        except (URLError, HTTPError, TimeoutError, OSError, Exception):
            pass  # Silently ignore - never block Claude

    thread = threading.Thread(target=_send, daemon=True)
    thread.start()
JIRA_KEY_RE = re.compile(r"[A-Z]+-[0-9]+")

LOOP_FLAG = Path.cwd() / ".claude" / ".ralph_loop_active"
STATE_FILE = Path.cwd() / ".claude" / "ralph-state.json"
PROMISE_FLAG_FILE = Path.cwd() / ".claude" / ".promise_done"
DEBUG_LOG = Path.cwd() / ".claude" / "stop-hook-debug.log"
GIT_GUARD_FILE = Path.cwd() / ".git" / "info" / "ralph-loop-active.json"


def _debug(msg: str) -> None:
    if os.environ.get("RALPH_STOP_HOOK_DEBUG") != "1":
        return
    DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(DEBUG_LOG, "a") as f:
        f.write(msg.rstrip() + "\n")


def _repo_id() -> str:
    try:
        return str(Path.cwd().resolve())
    except Exception:
        return str(Path.cwd())


def _read_json_dict(path: Path) -> dict[str, Any]:
    try:
        if not path.exists():
            return {}
        with open(path) as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_json_dict(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    tmp.replace(path)


def loop_guard_active() -> bool:
    """True if a loop has been activated and not cleared.

    This is intentionally independent of `.claude/.ralph_loop_active` so deleting
    that file cannot bypass enforcement once the loop has started.
    """
    state = _read_json_dict(STATE_FILE)
    if state.get("loop_active") is True:
        return True

    guard = _read_json_dict(GIT_GUARD_FILE)
    return guard.get("repo_id") == _repo_id() and guard.get("loop_active") is True


def ensure_loop_guard(hook_input: dict[str, Any]) -> None:
    """Persist loop-active state in STATE_FILE and (when available) GIT_GUARD_FILE."""
    state = _read_json_dict(STATE_FILE)
    state.setdefault("started_at", datetime.now().isoformat())
    state["loop_active"] = True
    transcript_path = hook_input.get("transcript_path") or hook_input.get("transcriptPath")
    if isinstance(transcript_path, str) and transcript_path:
        state["last_seen_transcript_path"] = transcript_path
    _write_json_dict(STATE_FILE, state)

    if GIT_GUARD_FILE.parent.exists():
        _write_json_dict(
            GIT_GUARD_FILE,
            {
                "repo_id": _repo_id(),
                "loop_active": True,
                "updated_at": datetime.now().isoformat(),
            },
        )

    # If the primary flag was deleted mid-loop, recreate it to prevent bypass.
    if not LOOP_FLAG.exists():
        try:
            LOOP_FLAG.parent.mkdir(parents=True, exist_ok=True)
            LOOP_FLAG.touch(exist_ok=True)
        except Exception:
            pass


def clear_loop_guard() -> None:
    """Clear persisted loop-active state after completion (or timeout)."""
    state = _read_json_dict(STATE_FILE)
    if state:
        state["loop_active"] = False
        state["completed_at"] = datetime.now().isoformat()
        _write_json_dict(STATE_FILE, state)

    for path in (GIT_GUARD_FILE, LOOP_FLAG, PROMISE_FLAG_FILE):
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        except Exception:
            # Cleanup is best-effort; never block exit due to cleanup failures.
            pass


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
    # Strongest signal: a persisted guard from an active loop.
    if loop_guard_active():
        return True

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
        path = Path(str(transcript_path)).expanduser()
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve()
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
    state = _read_json_dict(STATE_FILE)
    state.setdefault("started_at", datetime.now().isoformat())
    state["loop_active"] = True
    state["iterations"] = int(state.get("iterations", 0) or 0) + 1
    state["last_check"] = datetime.now().isoformat()
    _write_json_dict(STATE_FILE, state)

    iteration = int(state["iterations"])
    max_iterations = int(state.get("max_iterations", 25))

    # Notify monitor of iteration update
    _notify_monitor("task", {
        "action": "update",
        "iteration": iteration,
        "max_iterations": max_iterations,
        "step_desc": f"Checking exit conditions (iteration {iteration}/{max_iterations})...",
    })

    return iteration


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
            # If a loop is already active, missing input must not allow a bypass.
            if loop_guard_active() or LOOP_FLAG.exists():
                response = build_continue_message(
                    "Stop-hook invoked without input while loop is active.",
                    ["Try again and ensure a transcript is available."],
                )
                json.dump(response, sys.stderr)
                sys.exit(2)
            sys.exit(0)

        try:
            hook_input = json.loads(input_data)
        except json.JSONDecodeError:
            if loop_guard_active() or LOOP_FLAG.exists():
                response = build_continue_message(
                    "Stop-hook received invalid JSON while loop is active.",
                    ["Try again; do not attempt to bypass by breaking hook input."],
                )
                json.dump(response, sys.stderr)
                sys.exit(2)
            sys.exit(0)

        if not should_enforce_exit_policy(hook_input):
            sys.exit(0)

        active_loop = bool(loop_guard_active() or LOOP_FLAG.exists() or hook_input.get("completion_promise"))
        if active_loop:
            ensure_loop_guard(hook_input)

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
            if active_loop:
                clear_loop_guard()
            sys.exit(0)

        transcript = get_transcript_text(hook_input, scan_length)
        promise_found = isinstance(transcript, str) and completion_promise in transcript
        flag_found = active_loop and check_promise_flag_file(completion_promise)

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
        coverage_threshold = requirements.get("coverage_threshold")
        if coverage_threshold is not None:
            try:
                coverage_threshold = int(coverage_threshold)
            except Exception:
                coverage_threshold = None

        if tests_required and enforce_tools:
            # Notify monitor: running tests (Actions/CI node)
            _notify_monitor("node-state", {
                "node": "actions",
                "state": "active",
                "message": "Running pytest...",
            })

            pytest_cmd = [*tools["pytest"], "-q"]
            if coverage_threshold is not None:
                pytest_cmd.extend(
                    [
                        "--cov=.",
                        "--cov-report=term-missing",
                        f"--cov-fail-under={coverage_threshold}",
                    ]
                )
            code, out = run_cmd(pytest_cmd, timeout_s=180)
            if code != 0:
                failures.append("pytest failed")
                suggestions.append(f"Fix failing tests:\n{out}")
                _notify_monitor("event", {
                    "event_type": "error",
                    "message": "Tests failed",
                    "source": "stop-hook",
                })
            else:
                _notify_monitor("event", {
                    "event_type": "success",
                    "message": "Tests passed",
                    "source": "stop-hook",
                })

        if lint_required and enforce_tools:
            # Notify monitor: running linter
            _notify_monitor("node-state", {
                "node": "actions",
                "state": "active",
                "message": "Running ruff check...",
            })

            code, out = run_cmd([*tools["ruff"], "check", "."], timeout_s=120)
            if code != 0:
                failures.append("ruff check . failed")
                suggestions.append(f"Fix Ruff lint:\n{out}")
                _notify_monitor("event", {
                    "event_type": "error",
                    "message": "Lint check failed",
                    "source": "stop-hook",
                })

            code, out = run_cmd([*tools["ruff"], "format", "--check", "."], timeout_s=120)
            if code != 0:
                failures.append("ruff format --check . failed")
                suggestions.append(f"Run formatter:\n{out}")
            elif not failures:
                _notify_monitor("event", {
                    "event_type": "success",
                    "message": "Lint passed",
                    "source": "stop-hook",
                })

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

        # All checks passed - notify monitor of completion
        _notify_monitor("task", {"action": "complete"})
        _notify_monitor("event", {
            "event_type": "success",
            "message": "Task completed - all quality gates passed!",
            "source": "stop-hook",
        })

        if active_loop:
            clear_loop_guard()
        sys.exit(0)
    except Exception as e:
        # Fail-closed when enforcing (bypass vector); fail-open otherwise.
        if loop_guard_active() or LOOP_FLAG.exists():
            response = build_continue_message(
                "Stop-hook error while loop is active; continuing to avoid bypass.",
                [f"Error: {e}", "Fix the error and try again."],
            )
            json.dump(response, sys.stderr)
            sys.exit(2)

        json.dump({"decision": "allow", "action": "allow_exit_on_error", "error": str(e)}, sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
