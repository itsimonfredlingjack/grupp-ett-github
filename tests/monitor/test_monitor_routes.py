"""Tests for Monitor Routes."""

from unittest.mock import MagicMock

import pytest
from flask import Flask

from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def mock_socketio():
    """Create a mock SocketIO instance."""
    return MagicMock()


@pytest.fixture
def monitor_service():
    """Create a MonitorService instance."""
    return MonitorService()


@pytest.fixture
def app(monitor_service, mock_socketio):
    """Create a Flask app with monitor blueprint."""
    app = Flask(__name__)
    blueprint = create_monitor_blueprint(monitor_service, mock_socketio)
    app.register_blueprint(blueprint)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


class TestMonitorRoutes:
    """Tests for monitor API routes."""

    def test_get_state(self, client):
        """Test getting current state."""
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "current_node" in data
        assert "nodes" in data

    def test_update_state_valid(self, client, monitor_service, mock_socketio):
        """Test updating state with valid data."""
        payload = {"node": "jira", "state": "active", "message": "Testing"}
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 200

        assert monitor_service.current_node == "jira"
        assert monitor_service.nodes["jira"].message == "Testing"
        mock_socketio.emit.assert_called()

    def test_update_state_invalid_node(self, client):
        """Test updating with invalid node."""
        payload = {"node": "invalid", "state": "active"}
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_update_state_no_data(self, client):
        """Test updating with no data."""
        response = client.post("/api/monitor/state", json={})
        # Note: Depending on Flask version/config, this might be 400 if get_json fails
        # or if we check "if not data".
        assert response.status_code == 400

    def test_reset(self, client, monitor_service, mock_socketio):
        """Test resetting state."""
        monitor_service.update_node("jira", "active")

        response = client.post("/api/monitor/reset")
        assert response.status_code == 200

        assert monitor_service.current_node is None
        mock_socketio.emit.assert_called()

    def test_update_task(self, client, monitor_service, mock_socketio):
        """Test updating task info."""
        payload = {"title": "New Task", "status": "running"}
        response = client.post("/api/monitor/task", json=payload)
        assert response.status_code == 200

        info = monitor_service.get_task_info()
        assert info["title"] == "New Task"
        assert info["status"] == "running"
        # Check that start_time was auto-generated
        assert info["start_time"] is not None
        mock_socketio.emit.assert_called()

    def test_update_task_no_data(self, client):
        """Test updating task with no data."""
        response = client.post("/api/monitor/task", json={})
        assert response.status_code == 400
