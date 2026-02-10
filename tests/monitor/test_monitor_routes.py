"""Tests for Monitor Routes."""

from unittest.mock import MagicMock

import pytest
from flask import Flask

from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def monitor_service():
    return MonitorService()


@pytest.fixture
def mock_socketio():
    return MagicMock()


@pytest.fixture
def app(monitor_service, mock_socketio):
    app = Flask(__name__)
    app.config["TESTING"] = True
    blueprint = create_monitor_blueprint(monitor_service, mock_socketio)
    app.register_blueprint(blueprint)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestMonitorRoutes:
    """Tests for monitor API endpoints."""

    def test_get_state(self, client, monitor_service):
        """Test GET /api/monitor/state."""
        monitor_service.update_node("claude", "active", "Thinking")

        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()

        assert data["current_node"] == "claude"
        assert data["nodes"]["claude"]["message"] == "Thinking"

    def test_update_state_valid(self, client, monitor_service, mock_socketio):
        """Test POST /api/monitor/state with valid data."""
        payload = {"node": "github", "state": "active", "message": "Pushing"}
        response = client.post("/api/monitor/state", json=payload)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        # Verify service state
        state = monitor_service.get_state()
        assert state["current_node"] == "github"

        # Verify socket emission
        mock_socketio.emit.assert_called()

    def test_update_state_invalid_node(self, client):
        """Test POST /api/monitor/state with invalid node."""
        payload = {"node": "invalid", "state": "active"}
        response = client.post("/api/monitor/state", json=payload)

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid node" in data["error"]

    def test_update_state_no_json(self, client):
        """Test POST /api/monitor/state without JSON."""
        response = client.post("/api/monitor/state")
        assert response.status_code == 400

    def test_reset_monitoring(self, client, monitor_service, mock_socketio):
        """Test POST /api/monitor/reset."""
        monitor_service.update_node("claude", "active")

        response = client.post("/api/monitor/reset")
        assert response.status_code == 200

        state = monitor_service.get_state()
        assert state["current_node"] is None
        mock_socketio.emit.assert_called()

    def test_update_task(self, client, monitor_service, mock_socketio):
        """Test POST /api/monitor/task."""
        payload = {"title": "New Task", "status": "running"}
        response = client.post("/api/monitor/task", json=payload)

        assert response.status_code == 200

        info = monitor_service.get_task_info()
        assert info["title"] == "New Task"
        assert info["status"] == "running"
        assert info["start_time"] is not None  # Auto-generated
        mock_socketio.emit.assert_called()
