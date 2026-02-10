"""Tests for monitoring routes and service."""

from unittest.mock import MagicMock

import pytest
from flask_socketio import SocketIO

from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def monitor_service():
    """Create a monitor service instance."""
    return MonitorService()


@pytest.fixture
def socketio():
    """Create a mock SocketIO instance."""
    return MagicMock(spec=SocketIO)


@pytest.fixture
def app(monitor_service, socketio):
    """Create a Flask app with monitor blueprint."""
    from flask import Flask

    app = Flask(__name__)
    app.config["TESTING"] = True
    blueprint = create_monitor_blueprint(monitor_service, socketio)
    app.register_blueprint(blueprint)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


class TestMonitorRoutes:
    """Tests for monitor API routes."""

    def test_get_state(self, client, monitor_service):
        """Test fetching current state."""
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "nodes" in data
        assert "event_log" in data
        assert data["nodes"] == monitor_service.get_state()["nodes"]

    def test_update_state_valid(self, client, monitor_service, socketio):
        """Test updating node state."""
        payload = {"node": "jira", "state": "active", "message": "Fetching ticket"}
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 200

        state = monitor_service.get_state()
        assert state["nodes"]["jira"]["active"] is True
        assert state["nodes"]["jira"]["message"] == "Fetching ticket"
        assert state["current_node"] == "jira"

        # Verify socket emission
        socketio.emit.assert_called()

    def test_update_state_invalid_node(self, client):
        """Test updating with invalid node."""
        payload = {"node": "invalid_node", "state": "active"}
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 400
        assert "Invalid node" in response.get_json()["error"]

    def test_update_state_no_json(self, client):
        """Test updating without JSON."""
        response = client.post("/api/monitor/state")
        assert response.status_code == 400

    def test_reset_monitoring(self, client, monitor_service):
        """Test resetting monitoring state."""
        # First set some state
        monitor_service.update_node("claude", "active", "working")

        response = client.post("/api/monitor/reset")
        assert response.status_code == 200

        state = monitor_service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0

    def test_update_task(self, client, monitor_service):
        """Test updating task info."""
        payload = {"title": "Fix CI", "status": "running"}
        response = client.post("/api/monitor/task", json=payload)
        assert response.status_code == 200

        task_info = monitor_service.get_task_info()
        assert task_info["title"] == "Fix CI"
        assert task_info["status"] == "running"
        assert task_info["start_time"] is not None  # Auto-generated

    def test_update_task_no_json(self, client):
        """Test updating task without JSON."""
        response = client.post("/api/monitor/task")
        assert response.status_code == 400


class TestMonitorService:
    """Tests for MonitorService logic."""

    def test_initial_state(self, monitor_service):
        """Test initial empty state."""
        state = monitor_service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert all(not n["active"] for n in state["nodes"].values())

    def test_node_transition(self, monitor_service):
        """Test transitioning between nodes."""
        monitor_service.update_node("jira", "active")
        assert monitor_service.current_node == "jira"
        assert monitor_service.nodes["jira"].active is True

        monitor_service.update_node("claude", "active")
        assert monitor_service.current_node == "claude"
        assert monitor_service.nodes["claude"].active is True
        assert monitor_service.nodes["jira"].active is False  # Should be deactivated

    def test_event_log_limit(self, monitor_service):
        """Test event log size limit."""
        monitor_service.max_events = 5
        for i in range(10):
            monitor_service.add_event("jira", f"msg {i}")

        assert len(monitor_service.event_log) == 5
        assert monitor_service.event_log[-1]["message"] == "msg 9"
