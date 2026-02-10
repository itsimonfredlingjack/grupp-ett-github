"""Tests for monitoring routes."""

from unittest.mock import Mock, patch

import pytest
from flask import Flask

from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def monitor_service():
    """Fixture for MonitorService."""
    return MonitorService()


@pytest.fixture
def socketio():
    """Fixture for SocketIO mock."""
    return Mock()


@pytest.fixture
def app(monitor_service, socketio):
    """Fixture for Flask app with monitor blueprint."""
    app = Flask(__name__)
    blueprint = create_monitor_blueprint(monitor_service, socketio)
    app.register_blueprint(blueprint)
    return app


@pytest.fixture
def client(app):
    """Fixture for test client."""
    return app.test_client()


class TestMonitorRoutes:
    """Tests for monitoring API endpoints."""

    def test_get_state(self, client, monitor_service):
        """Test GET /api/monitor/state."""
        monitor_service.update_node("claude", "active", "Testing")

        response = client.get("/api/monitor/state")

        assert response.status_code == 200
        data = response.get_json()
        assert data["current_node"] == "claude"
        assert len(data["event_log"]) == 1

    def test_update_state_valid(self, client, socketio):
        """Test POST /api/monitor/state with valid data."""
        payload = {"node": "claude", "state": "active", "message": "Working hard"}

        response = client.post("/api/monitor/state", json=payload)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] == "claude"

        # Verify socket emission
        assert socketio.emit.called
        args, kwargs = socketio.emit.call_args
        assert args[0] == "state_update"

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
        data = response.get_json()
        assert "No JSON data" in data["error"]

    def test_reset_monitoring(self, client, monitor_service, socketio):
        """Test POST /api/monitor/reset."""
        monitor_service.update_node("jira", "active")

        response = client.post("/api/monitor/reset")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] is None

        assert socketio.emit.called

    def test_update_task(self, client, socketio):
        """Test POST /api/monitor/task."""
        payload = {"title": "New Feature", "status": "running"}

        response = client.post("/api/monitor/task", json=payload)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["task_info"]["title"] == "New Feature"
        # Should set default time
        assert data["current_state"]["task_info"]["start_time"] is not None

        assert socketio.emit.called

    def test_update_task_no_json(self, client):
        """Test POST /api/monitor/task without JSON."""
        response = client.post("/api/monitor/task")

        assert response.status_code == 400

    def test_server_error_handling(self, client, monitor_service):
        """Test error handling in routes."""
        # Mock get_state to raise exception
        with patch.object(
            monitor_service, "get_state", side_effect=Exception("Database error")
        ):
            response = client.get("/api/monitor/state")
            assert response.status_code == 500
            data = response.get_json()
            assert data["success"] is False
            assert "Database error" in data["error"]
