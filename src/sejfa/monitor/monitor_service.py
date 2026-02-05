"""Monitor Service - Core state management for Ralph Loop monitoring.

This service manages:
- Task state (current step, iteration, progress)
- Event log (actions performed during the loop)
- WebSocket client connections for real-time updates
"""

from __future__ import annotations

import re
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Step definitions matching the 5-node orbital visualization.
STEPS = [
    {"name": "Jira Ticket", "desc": "Fetching ticket requirements..."},
    {"name": "Claude Code", "desc": "Writing tests and implementation..."},
    {"name": "GitHub PR", "desc": "Pushing code and creating PR..."},
    {"name": "Jules Review", "desc": "AI reviewing code changes..."},
    {"name": "CI Pipeline", "desc": "Running tests and validation..."},
]


@dataclass
class TaskState:
    """Current task state for monitoring."""

    task_id: str = ""
    title: str = ""
    step: int = 0
    step_name: str = ""
    step_desc: str = ""
    status: str = "pending"  # pending, in_progress, done, failed
    iteration: int = 0
    max_iterations: int = 25
    branch: str = ""
    started_at: datetime | None = None
    elapsed_seconds: int = 0


@dataclass
class Event:
    """Event logged during task execution."""

    event_type: str  # info, success, warning, error
    message: str
    source: str = "claude"
    timestamp: datetime = field(default_factory=datetime.now)
    task_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "event_type": self.event_type,
            "message": self.message,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "task_id": self.task_id,
            "metadata": self.metadata,
        }


class MonitorService:
    """Service for managing Ralph Loop monitoring state.

    Thread-safe singleton that maintains current task state and event history.
    """

    _instance: MonitorService | None = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> MonitorService:
        """Create or return the singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the service (only once for singleton)."""
        if getattr(self, "_initialized", False):
            return

        self._task: TaskState = TaskState()
        self._events: list[Event] = []
        self._status: str = "idle"  # idle, running, paused
        self._clients: set[Any] = set()
        self._timer_thread: threading.Thread | None = None
        self._timer_running: bool = False
        self._state_lock: threading.Lock = threading.Lock()
        self._initialized = True

    def get_state(self) -> dict[str, Any]:
        """Get current full state for dashboard initialization."""
        with self._state_lock:
            return {
                "task": self._task_to_dict() if self._task.task_id else None,
                "events": [e.to_dict() for e in self._events[-20:]],  # Last 20
                "status": self._status,
                "elapsed_seconds": self._task.elapsed_seconds,
            }

    def _task_to_dict(self) -> dict[str, Any]:
        """Convert current task state to dictionary."""
        step_index = self._task.step
        if step_index < 0 or step_index >= len(STEPS):
            step_index = 0

        return {
            "task_id": self._task.task_id,
            "title": self._task.title,
            "step": self._task.step,
            "step_name": self._task.step_name or STEPS[step_index]["name"],
            "step_desc": self._task.step_desc or STEPS[step_index]["desc"],
            "status": self._task.status,
            "iteration": self._task.iteration,
            "max_iterations": self._task.max_iterations,
            "branch": self._task.branch,
        }

    def start_task(
        self,
        task_id: str,
        title: str = "",
        branch: str = "",
        max_iterations: int = 25,
    ) -> dict[str, Any]:
        """Start tracking a new task."""
        with self._state_lock:
            self._task = TaskState(
                task_id=task_id,
                title=title,
                step=0,
                step_name=STEPS[0]["name"],
                step_desc=STEPS[0]["desc"],
                status="in_progress",
                iteration=0,
                max_iterations=max_iterations,
                branch=branch,
                started_at=datetime.now(),
                elapsed_seconds=0,
            )
            self._status = "running"
            self._events = []  # Clear previous events

            # Start timer
            self._start_timer()

            # Add start event
            self._add_event_internal(
                Event(
                    event_type="info",
                    message=f"Task {task_id} started",
                    source="monitor",
                    task_id=task_id,
                )
            )

            return self._task_to_dict()

    def update_task(
        self,
        step: int | None = None,
        step_name: str | None = None,
        step_desc: str | None = None,
        status: str | None = None,
        iteration: int | None = None,
    ) -> dict[str, Any]:
        """Update current task state."""
        with self._state_lock:
            if step is not None and 0 <= step < len(STEPS):
                self._task.step = step
                self._task.step_name = step_name or STEPS[step]["name"]
                self._task.step_desc = step_desc or STEPS[step]["desc"]
            elif step_name:
                self._task.step_name = step_name
            elif step_desc:
                self._task.step_desc = step_desc

            if status:
                self._task.status = status
                if status == "done":
                    self._status = "idle"
                    self._stop_timer()
                elif status == "failed":
                    self._status = "idle"
                    self._stop_timer()

            if iteration is not None:
                self._task.iteration = iteration

            return self._task_to_dict()

    def complete_task(self) -> dict[str, Any]:
        """Mark current task as complete."""
        with self._state_lock:
            self._task.status = "done"
            self._task.step = len(STEPS) - 1
            self._task.step_name = STEPS[-1]["name"]
            self._task.step_desc = "Task completed successfully!"
            self._status = "idle"
            self._stop_timer()

            self._add_event_internal(
                Event(
                    event_type="success",
                    message=f"Task {self._task.task_id} completed",
                    source="monitor",
                    task_id=self._task.task_id,
                )
            )

            return self._task_to_dict()

    def fail_task(self, reason: str = "") -> dict[str, Any]:
        """Mark current task as failed."""
        with self._state_lock:
            self._task.status = "failed"
            self._task.step_desc = reason or "Task failed"
            self._status = "idle"
            self._stop_timer()

            self._add_event_internal(
                Event(
                    event_type="error",
                    message=f"Task {self._task.task_id} failed: {reason}",
                    source="monitor",
                    task_id=self._task.task_id,
                )
            )

            return self._task_to_dict()

    def reset(self) -> None:
        """Reset monitor state."""
        with self._state_lock:
            self._task = TaskState()
            self._events = []
            self._status = "idle"
            self._stop_timer()

    def add_event(
        self,
        event_type: str,
        message: str,
        source: str = "claude",
        task_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Event:
        """Add an event to the log."""
        with self._state_lock:
            event = Event(
                event_type=event_type,
                message=message,
                source=source,
                task_id=task_id or self._task.task_id,
                metadata=metadata or {},
            )
            return self._add_event_internal(event)

    def _add_event_internal(self, event: Event) -> Event:
        """Add event (must be called within lock)."""
        self._events.append(event)
        # Keep max 100 events
        if len(self._events) > 100:
            self._events = self._events[-100:]
        return event

    def get_events(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get recent events."""
        with self._state_lock:
            return [e.to_dict() for e in self._events[-limit:]]

    def _start_timer(self) -> None:
        """Start elapsed time counter."""
        if self._timer_running:
            return

        self._timer_running = True

        def timer_loop() -> None:
            while self._timer_running:
                threading.Event().wait(1)  # Sleep 1 second
                if self._timer_running and self._status == "running":
                    with self._state_lock:
                        self._task.elapsed_seconds += 1

        self._timer_thread = threading.Thread(target=timer_loop, daemon=True)
        self._timer_thread.start()

    def _stop_timer(self) -> None:
        """Stop elapsed time counter."""
        self._timer_running = False

    # Methods for parsing CURRENT_TASK.md
    def parse_current_task(
        self, task_file_path: str | Path | None = None
    ) -> dict[str, Any] | None:
        """Parse CURRENT_TASK.md for Ralph Loop state.

        Args:
            task_file_path: Path to CURRENT_TASK.md (defaults to docs/CURRENT_TASK.md)

        Returns:
            Dict with parsed state or None if file doesn't exist
        """
        if task_file_path is None:
            # Try common locations
            candidates = [
                Path.cwd() / "CURRENT_TASK.md",
                Path.cwd() / "docs" / "CURRENT_TASK.md",
            ]
            for candidate in candidates:
                if candidate.exists():
                    task_file_path = candidate
                    break

        if task_file_path is None:
            return None

        path = Path(task_file_path)
        if not path.exists():
            return None

        try:
            content = path.read_text(encoding="utf-8")

            # Extract iteration count
            iteration_match = re.search(r"Iteration[:\s]+(\d+)", content, re.IGNORECASE)
            iteration = int(iteration_match.group(1)) if iteration_match else 0

            # Count checked criteria
            checked = content.count("[x]") + content.count("[X]")
            total = content.count("[ ]") + checked

            # Extract task ID (e.g., GE-123, PROJ-456)
            task_id_match = re.search(r"([A-Z]+-\d+)", content)
            task_id = task_id_match.group(1) if task_id_match else ""

            return {
                "active": True,
                "iteration": iteration,
                "criteria_checked": checked,
                "criteria_total": total,
                "task_id": task_id,
            }
        except Exception:
            return None

    # Tool-to-step mapping for hook integration
    @staticmethod
    def tool_to_step(tool_name: str) -> tuple[int, str]:
        """Map Claude Code tool name to workflow step.

        Args:
            tool_name: Name of the tool being used (Read, Edit, Bash, etc.)

        Returns:
            Tuple of (step_index, step_description)
        """
        tool_map = {
            # Reading/analyzing = Jira step
            "Read": (0, "Reading file..."),
            "Grep": (0, "Searching code..."),
            "Glob": (0, "Finding files..."),
            # Writing/creating = Claude step
            "Edit": (1, "Editing code..."),
            "Write": (1, "Writing file..."),
            "Task": (1, "Delegating to subagent..."),
            # Git operations = GitHub step
            "git commit": (2, "Committing changes..."),
            "git push": (2, "Pushing to remote..."),
            "gh pr create": (2, "Creating pull request..."),
            # Running tests = CI step
            "Bash": (4, "Running command..."),
            "pytest": (4, "Running tests..."),
            "ruff": (4, "Running linter..."),
            "npm test": (4, "Running tests..."),
        }

        # Check for exact match first
        if tool_name in tool_map:
            return tool_map[tool_name]

        # Check for partial matches (e.g., "git push origin" matches "git push")
        for key, value in tool_map.items():
            if tool_name.startswith(key):
                return value

        # Default to Claude step for unknown tools
        return (1, f"Using {tool_name}...")
