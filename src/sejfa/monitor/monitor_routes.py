"""Monitor Routes - REST API and WebSocket endpoints for dashboard.

Provides endpoints for:
- GET /api/monitor/state - Current full state
- POST /api/monitor/task - Start/update/complete task
- POST /api/monitor/event - Add event
- GET /api/monitor/ralph-state - Parse CURRENT_TASK.md
- WebSocket /ws - Real-time updates
"""

from __future__ import annotations

from typing import Any

from flask import Blueprint, Response, jsonify, request

from src.sejfa.monitor.monitor_service import MonitorService

_socketio_instance: Any | None = None


def _emit(event_name: str, payload: dict[str, Any]) -> None:
    """Broadcast event to all connected Socket.IO clients when available."""
    if _socketio_instance is not None:
        _socketio_instance.emit(event_name, payload)


def create_monitor_blueprint() -> Blueprint:
    """Create and configure the monitor blueprint.

    Returns:
        Flask Blueprint for monitor routes
    """
    bp = Blueprint("monitor", __name__)
    service = MonitorService()

    @bp.route("/api/monitor/state", methods=["GET"])
    def get_state() -> tuple[Response, int]:
        """Get current full monitor state.

        Returns:
            JSON with task, events, status, and elapsed_seconds
        """
        return jsonify(service.get_state()), 200

    @bp.route("/api/monitor/task", methods=["POST"])
    def handle_task() -> tuple[Response, int]:
        """Handle task actions (start, update, complete, fail, reset).

        Expected JSON body:
        - action: "start" | "update" | "complete" | "fail" | "reset"
        - task_id: Required for start action
        - title, branch, max_iterations: Optional for start
        - step, step_name, step_desc, status, iteration: Optional for update
        - step_desc (reason): Optional for fail

        Returns:
            JSON with updated task state
        """
        data = request.get_json() or {}
        action = data.get("action", "update")

        if action == "start":
            task_id = data.get("task_id")
            if not task_id:
                return jsonify({"error": "task_id required for start"}), 400

            result = service.start_task(
                task_id=task_id,
                title=data.get("title", ""),
                branch=data.get("branch", ""),
                max_iterations=data.get("max_iterations", 25),
            )
            _emit("task_update", {"type": "task_update", "data": result})
            return jsonify(result), 200

        elif action == "update":
            result = service.update_task(
                step=data.get("step"),
                step_name=data.get("step_name"),
                step_desc=data.get("step_desc"),
                status=data.get("status"),
                iteration=data.get("iteration"),
            )
            _emit("task_update", {"type": "task_update", "data": result})
            return jsonify(result), 200

        elif action == "complete":
            result = service.complete_task()
            _emit("task_update", {"type": "task_update", "data": result})
            return jsonify(result), 200

        elif action == "fail":
            result = service.fail_task(data.get("step_desc", ""))
            _emit("task_update", {"type": "task_update", "data": result})
            return jsonify(result), 200

        elif action == "reset":
            service.reset()
            _emit("reset", {"type": "reset"})
            return jsonify({"status": "reset"}), 200

        else:
            return jsonify({"error": f"Unknown action: {action}"}), 400

    @bp.route("/api/monitor/event", methods=["POST"])
    def add_event() -> tuple[Response, int]:
        """Add an event to the log.

        Expected JSON body:
        - event_type: "info" | "success" | "warning" | "error"
        - message: Event message
        - source: Optional source identifier (default: "claude")
        - task_id: Optional task ID
        - metadata: Optional additional data

        Returns:
            JSON with the created event
        """
        data = request.get_json() or {}

        event_type = data.get("event_type", "info")
        message = data.get("message")

        if not message:
            return jsonify({"error": "message required"}), 400

        event = service.add_event(
            event_type=event_type,
            message=message,
            source=data.get("source", "claude"),
            task_id=data.get("task_id"),
            metadata=data.get("metadata"),
        )
        _emit("event", {"type": "event", "data": event.to_dict()})
        return jsonify(event.to_dict()), 201

    @bp.route("/api/monitor/ralph-state", methods=["GET"])
    def get_ralph_state() -> tuple[Response, int]:
        """Parse CURRENT_TASK.md for Ralph Loop state.

        Returns:
            JSON with iteration, criteria progress, task_id
        """
        result = service.parse_current_task()
        if result is None:
            return jsonify({"active": False}), 200
        return jsonify(result), 200

    @bp.route("/api/monitor/node-state", methods=["POST"])
    def update_node_state() -> tuple[Response, int]:
        """Update which node is active (for hook integration).

        Expected JSON body:
        - node: "jira" | "claude" | "github" | "actions" | "jules" | "merge"
        - state: "active" | "done" | "pending"
        - message: Optional status message

        Returns:
            JSON with updated task state
        """
        data = request.get_json() or {}
        node = data.get("node", "").lower()
        message = data.get("message", "")

        # Map node names to step indices
        node_to_step = {
            "jira": 0,
            "claude": 1,
            "github": 2,
            "jules": 3,
            "actions": 4,
            "ci": 4,
        }

        step = node_to_step.get(node)
        if step is None:
            return jsonify({"error": f"Unknown node: {node}"}), 400

        result = service.update_task(step=step, step_desc=message or None)
        _emit("task_update", {"type": "task_update", "data": result})

        # Also add an event
        event = service.add_event(
            event_type="info",
            message=message or f"Active: {node.upper()}",
            source=node,
        )
        _emit("event", {"type": "event", "data": event.to_dict()})

        return jsonify(result), 200

    return bp


def create_socketio_handlers(socketio: Any) -> None:
    """Register SocketIO event handlers for real-time updates.

    Args:
        socketio: Flask-SocketIO instance
    """
    global _socketio_instance
    _socketio_instance = socketio

    service = MonitorService()

    @socketio.on("connect")
    def handle_connect() -> None:
        """Handle new WebSocket connection."""
        # Send current state on connect
        socketio.emit("init", {"type": "init", "data": service.get_state()})

    @socketio.on("disconnect")
    def handle_disconnect() -> None:
        """Handle WebSocket disconnection."""
        pass

    @socketio.on("ping")
    def handle_ping() -> None:
        """Handle heartbeat ping."""
        socketio.emit("pong", {"type": "pong"})

    @socketio.on("get_state")
    def handle_get_state() -> None:
        """Handle state request."""
        socketio.emit("init", {"type": "init", "data": service.get_state()})


def broadcast_task_update(socketio: Any, task_data: dict[str, Any]) -> None:
    """Broadcast task update to all connected clients.

    Args:
        socketio: Flask-SocketIO instance
        task_data: Task state dictionary
    """
    socketio.emit("task_update", {"type": "task_update", "data": task_data})


def broadcast_event(socketio: Any, event_data: dict[str, Any]) -> None:
    """Broadcast event to all connected clients.

    Args:
        socketio: Flask-SocketIO instance
        event_data: Event dictionary
    """
    socketio.emit("event", {"type": "event", "data": event_data})
