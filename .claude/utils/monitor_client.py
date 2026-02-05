#!/usr/bin/env python3
"""
Monitor Client - Lightweight HTTP client for the Ralph Loop Monitor API.

Used by hooks and commands to send events and task updates to the monitor.
All methods are non-blocking (fire-and-forget via background threads).
All failures are silently ignored to never block Claude.

Usage:
    from monitor_client import send_event, send_task_start, send_task_update

    # Send an event
    send_event("info", "Starting implementation", source="claude")

    # Start task tracking
    send_task_start("GE-123", title="Add user authentication")

    # Update step
    send_task_update("GE-123", step=1, step_name="Claude Code", step_desc="Writing tests...")
"""

from __future__ import annotations

import atexit
import json
import os
import threading
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Default to localhost for local development
# Can be overridden via environment variable
MONITOR_BASE_URL = os.environ.get("MONITOR_URL", "http://localhost:5000")
TIMEOUT_SECONDS = 3

# Track pending threads so we can wait for them on exit
_pending_threads: list[threading.Thread] = []


def _flush_pending() -> None:
    """Wait for pending sends to complete before process exits (max 2s)."""
    for t in _pending_threads:
        t.join(timeout=2)
    _pending_threads.clear()


atexit.register(_flush_pending)


_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "RalphMonitor/1.0 (claude-hook)",
    "Accept": "application/json",
}


def _post(url: str, payload: dict) -> None:
    """POST JSON to URL. Blocks until complete or timeout."""
    try:
        data = json.dumps(payload).encode("utf-8")
        request = Request(url, data=data, headers=_HEADERS, method="POST")
        with urlopen(request, timeout=TIMEOUT_SECONDS):
            pass
    except (URLError, HTTPError, TimeoutError, OSError, Exception):
        pass  # Silently ignore all errors


def _post_async(url: str, payload: dict) -> None:
    """POST in a background thread (non-blocking). Ensures delivery on exit."""
    thread = threading.Thread(target=_post, args=(url, payload), daemon=True)
    _pending_threads.append(thread)
    thread.start()


# ════════════════════════════════════════════════════════════════
# Public API - Event Methods
# ════════════════════════════════════════════════════════════════


def send_event(
    event_type: str,
    message: str,
    source: str = "claude",
    task_id: str | None = None,
    metadata: dict | None = None,
) -> None:
    """Send an event to the monitor (non-blocking).

    Args:
        event_type: Type of event ("info", "success", "warning", "error")
        message: Event message
        source: Source identifier (default: "claude")
        task_id: Optional task ID
        metadata: Optional additional data
    """
    payload: dict = {
        "event_type": event_type,
        "message": message,
        "source": source,
    }
    if task_id:
        payload["task_id"] = task_id
    if metadata:
        payload["metadata"] = metadata

    _post_async(f"{MONITOR_BASE_URL}/api/monitor/event", payload)


# ════════════════════════════════════════════════════════════════
# Public API - Task Methods
# ════════════════════════════════════════════════════════════════


def send_task_start(
    task_id: str,
    title: str = "",
    branch: str | None = None,
    max_iterations: int = 25,
) -> None:
    """Notify monitor that a task has started (non-blocking).

    Args:
        task_id: Jira ticket ID (e.g., "GE-123")
        title: Task title/summary
        branch: Git branch name
        max_iterations: Maximum Ralph Loop iterations
    """
    payload: dict = {
        "task_id": task_id,
        "action": "start",
        "title": title,
        "step": 0,
        "step_name": "Jira Ticket",
        "step_desc": "Fetching ticket requirements...",
        "max_iterations": max_iterations,
    }
    if branch:
        payload["branch"] = branch

    _post_async(f"{MONITOR_BASE_URL}/api/monitor/task", payload)


def send_task_update(
    task_id: str,
    step: int | None = None,
    step_name: str | None = None,
    step_desc: str | None = None,
    status: str | None = None,
    iteration: int | None = None,
) -> None:
    """Update task state on the monitor (non-blocking).

    Args:
        task_id: Jira ticket ID
        step: Step index (0=Jira, 1=Claude, 2=GitHub, 3=Jules, 4=Actions)
        step_name: Custom step name
        step_desc: Custom step description
        status: Task status ("pending", "in_progress", "done", "failed")
        iteration: Current Ralph Loop iteration
    """
    payload: dict = {
        "task_id": task_id,
        "action": "update",
    }
    if step is not None:
        payload["step"] = step
    if step_name:
        payload["step_name"] = step_name
    if step_desc:
        payload["step_desc"] = step_desc
    if status:
        payload["status"] = status
    if iteration is not None:
        payload["iteration"] = iteration

    _post_async(f"{MONITOR_BASE_URL}/api/monitor/task", payload)


def send_task_complete(task_id: str) -> None:
    """Notify monitor that a task completed (non-blocking).

    Args:
        task_id: Jira ticket ID
    """
    _post_async(
        f"{MONITOR_BASE_URL}/api/monitor/task",
        {
            "task_id": task_id,
            "action": "complete",
        },
    )


def send_task_fail(task_id: str, reason: str = "") -> None:
    """Notify monitor that a task failed (non-blocking).

    Args:
        task_id: Jira ticket ID
        reason: Failure reason
    """
    _post_async(
        f"{MONITOR_BASE_URL}/api/monitor/task",
        {
            "task_id": task_id,
            "action": "fail",
            "step_desc": reason,
        },
    )


def send_task_reset() -> None:
    """Reset the monitor task state (non-blocking)."""
    _post_async(
        f"{MONITOR_BASE_URL}/api/monitor/task",
        {
            "task_id": "_",
            "action": "reset",
        },
    )


# ════════════════════════════════════════════════════════════════
# Public API - Node State Methods (for hook integration)
# ════════════════════════════════════════════════════════════════


def send_node_active(
    node: str,
    message: str = "",
    task_id: str | None = None,
) -> None:
    """Update which node is active on the monitor (non-blocking).

    Args:
        node: Node name ("jira", "claude", "github", "jules", "actions")
        message: Optional status message
        task_id: Optional task ID
    """
    payload: dict = {
        "node": node,
        "state": "active",
        "message": message,
    }
    if task_id:
        payload["task_id"] = task_id

    _post_async(f"{MONITOR_BASE_URL}/api/monitor/node-state", payload)


# ════════════════════════════════════════════════════════════════
# Tool-to-Node Mapping (for pre-tool-use hook)
# ════════════════════════════════════════════════════════════════

TOOL_NODE_MAP = {
    # Reading/analyzing = Jira step
    "Read": ("jira", "Reading file..."),
    "Grep": ("jira", "Searching code..."),
    "Glob": ("jira", "Finding files..."),
    # Writing/creating = Claude step
    "Edit": ("claude", "Editing code..."),
    "Write": ("claude", "Writing file..."),
    "Task": ("claude", "Delegating to subagent..."),
    # Running commands = Actions step (CI)
    "Bash": ("actions", "Running command..."),
}

# Command patterns for Bash tool
COMMAND_NODE_MAP = {
    "git commit": ("github", "Committing changes..."),
    "git push": ("github", "Pushing to remote..."),
    "gh pr create": ("github", "Creating pull request..."),
    "pytest": ("actions", "Running tests..."),
    "ruff": ("actions", "Running linter..."),
    "npm test": ("actions", "Running tests..."),
}


def notify_tool_use(tool_name: str, command: str | None = None) -> None:
    """Send monitor notification based on tool being used.

    Args:
        tool_name: Name of the Claude Code tool (Read, Edit, Bash, etc.)
        command: For Bash tool, the command being run
    """
    # Check for specific commands first (for Bash tool)
    if command:
        for pattern, (node, msg) in COMMAND_NODE_MAP.items():
            if pattern in command:
                send_node_active(node, msg)
                return

    # Fall back to tool mapping
    if tool_name in TOOL_NODE_MAP:
        node, msg = TOOL_NODE_MAP[tool_name]
        send_node_active(node, msg)


# ════════════════════════════════════════════════════════════════
# CLI Interface (for testing)
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: monitor_client.py <command> [args...]")
        print("Commands:")
        print("  event <type> <message> [source]")
        print("  start <task_id> [title]")
        print("  update <task_id> <step>")
        print("  complete <task_id>")
        print("  fail <task_id> [reason]")
        print("  reset")
        print("  node <node> [message]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "event" and len(sys.argv) >= 4:
        send_event(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "cli")
    elif command == "start" and len(sys.argv) >= 3:
        send_task_start(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    elif command == "update" and len(sys.argv) >= 4:
        send_task_update(sys.argv[2], step=int(sys.argv[3]))
    elif command == "complete" and len(sys.argv) >= 3:
        send_task_complete(sys.argv[2])
    elif command == "fail" and len(sys.argv) >= 3:
        send_task_fail(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    elif command == "reset":
        send_task_reset()
    elif command == "node" and len(sys.argv) >= 3:
        send_node_active(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    else:
        print(f"Unknown command or missing arguments: {command}")
        sys.exit(1)

    # Wait for async operations to complete
    _flush_pending()
    print("Done")
