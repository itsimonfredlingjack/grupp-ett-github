"""Tests for Monitor API routes."""

from unittest.mock import MagicMock

import pytest
from flask import Flask

from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def app():
    """Create a Flask app with monitor blueprint."""
    app = Flask(__name__)
    service = MonitorService()
    socketio = MagicMock()
    app.register_blueprint(create_monitor_blueprint(service, socketio))
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


class TestMonitorRoutes:
    """Tests for monitoring endpoints."""

    def test_get_state(self, client):
        """Test GET /api/monitor/state."""
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "nodes" in data
        assert "event_log" in data

    def test_update_state(self, client):
        """Test POST /api/monitor/state."""
        response = client.post(
            "/api/monitor/state",
            json={"node": "jira", "state": "active", "message": "Processing"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] == "jira"

    def test_update_state_invalid_node(self, client):
        """Test POST /api/monitor/state with invalid node."""
        response = client.post(
            "/api/monitor/state", json={"node": "invalid", "state": "active"}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_reset_monitoring(self, client):
        """Test POST /api/monitor/reset."""
        # First set state
        client.post("/api/monitor/state", json={"node": "jira", "state": "active"})

        # Then reset
        response = client.post("/api/monitor/reset")
        assert response.status_code == 200

        # Verify reset
        state_response = client.get("/api/monitor/state")
        state = state_response.get_json()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0

    def test_update_task(self, client):
        """Test POST /api/monitor/task."""
        response = client.post(
            "/api/monitor/task", json={"title": "My Task", "status": "running"}
        )
        assert response.status_code == 200

        state_response = client.get("/api/monitor/state")
        state = state_response.get_json()
        assert state["task_info"]["title"] == "My Task"
