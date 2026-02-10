"""Tests for MonitorService and Monitor Routes."""

import json
from unittest.mock import MagicMock

import pytest
from flask import Flask

from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def monitor_service():
    """Fixture for MonitorService."""
    return MonitorService()


class TestMonitorService:
    """Tests for MonitorService class."""

    def test_initial_state(self, monitor_service):
        """Test initial state of MonitorService."""
        state = monitor_service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"
        assert len(state["nodes"]) == 5  # jira, claude, github, jules, actions

    def test_update_node_valid(self, monitor_service):
        """Test updating a valid node."""
        success = monitor_service.update_node("jira", "active", "Fetching ticket")
        assert success is True

        state = monitor_service.get_state()
        assert state["current_node"] == "jira"
        assert state["nodes"]["jira"]["active"] is True
        assert state["nodes"]["jira"]["message"] == "Fetching ticket"
        assert len(state["event_log"]) == 1
        assert state["event_log"][0]["node"] == "jira"

    def test_update_node_invalid(self, monitor_service):
        """Test updating an invalid node."""
        success = monitor_service.update_node("invalid_node", "active")
        assert success is False
        assert monitor_service.current_node is None

    def test_node_transition(self, monitor_service):
        """Test transitioning from one node to another."""
        monitor_service.update_node("jira", "active")
        assert monitor_service.current_node == "jira"
        assert monitor_service.nodes["jira"].active is True

        monitor_service.update_node("claude", "active")
        assert monitor_service.current_node == "claude"
        assert monitor_service.nodes["claude"].active is True
        assert monitor_service.nodes["jira"].active is False  # Previous node deactivated

    def test_reset(self, monitor_service):
        """Test resetting the service."""
        monitor_service.update_node("jira", "active")
        monitor_service.set_task_info("Task 1", "running")

        monitor_service.reset()

        state = monitor_service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"

    def test_set_task_info(self, monitor_service):
        """Test setting task info."""
        monitor_service.set_task_info("New Task", "running", "2023-01-01T00:00:00Z")

        info = monitor_service.get_task_info()
        assert info["title"] == "New Task"
        assert info["status"] == "running"
        assert info["start_time"] == "2023-01-01T00:00:00Z"

    def test_event_log_limit(self, monitor_service):
        """Test that event log respects max_events."""
        monitor_service.max_events = 5
        for i in range(10):
            monitor_service.add_event("claude", f"Message {i}")

        assert len(monitor_service.event_log) == 5
        assert monitor_service.event_log[-1]["message"] == "Message 9"


class TestMonitorRoutes:
    """Tests for Monitor API routes."""

    @pytest.fixture
    def app(self, monitor_service):
        """Fixture for Flask app with monitor blueprint."""
        app = Flask(__name__)
        socketio_mock = MagicMock()
        blueprint = create_monitor_blueprint(monitor_service, socketio_mock)
        app.register_blueprint(blueprint)
        app.socketio_mock = socketio_mock  # Attach for verification
        return app

    @pytest.fixture
    def client(self, app):
        """Fixture for test client."""
        return app.test_client()

    def test_get_state(self, client):
        """Test GET /api/monitor/state."""
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "nodes" in data
        assert "event_log" in data

    def test_update_state_valid(self, client, app):
        """Test POST /api/monitor/state with valid data."""
        payload = {"node": "jira", "state": "active", "message": "Working"}
        response = client.post("/api/monitor/state", json=payload)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] == "jira"

        # Verify socket emission
        app.socketio_mock.emit.assert_called()

    def test_update_state_invalid_node(self, client):
        """Test POST /api/monitor/state with invalid node."""
        payload = {"node": "invalid", "state": "active"}
        response = client.post("/api/monitor/state", json=payload)

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid node" in data["error"]

    def test_update_state_no_json(self, client):
        """Test POST /api/monitor/state with no JSON."""
        response = client.post("/api/monitor/state")
        assert response.status_code == 400

    def test_reset_monitoring(self, client, app):
        """Test POST /api/monitor/reset."""
        # First set some state
        client.post("/api/monitor/state", json={"node": "jira", "state": "active"})

        response = client.post("/api/monitor/reset")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] is None

        # Verify socket emission
        app.socketio_mock.emit.assert_called()

    def test_update_task(self, client, app):
        """Test POST /api/monitor/task."""
        payload = {
            "title": "Fix Bug",
            "status": "running"
        }
        response = client.post("/api/monitor/task", json=payload)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        task_info = data["current_state"]["task_info"]
        assert task_info["title"] == "Fix Bug"
        assert task_info["status"] == "running"
        assert task_info["start_time"] is not None  # Should auto-set

        # Verify socket emission
        app.socketio_mock.emit.assert_called()

    def test_update_task_no_json(self, client):
        """Test POST /api/monitor/task with no JSON."""
        response = client.post("/api/monitor/task")
        assert response.status_code == 400
