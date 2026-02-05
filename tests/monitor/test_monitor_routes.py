"""Tests for monitor routes."""

import pytest
from flask import Flask
from flask_socketio import SocketIO

from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def app():
    """Create test Flask app."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test-secret"
    return app


@pytest.fixture
def socketio(app):
    """Create socketio instance."""
    return SocketIO(app, cors_allowed_origins="*")


@pytest.fixture
def monitor_service():
    """Create monitor service."""
    return MonitorService()


@pytest.fixture
def client(app, socketio, monitor_service):
    """Create test client with monitor blueprint."""
    blueprint = create_monitor_blueprint(monitor_service, socketio)
    app.register_blueprint(blueprint)
    return app.test_client()


class TestMonitorRoutes:
    """Test monitor routes."""

    def test_get_state(self, client):
        """GET /api/monitor/state should return 200 and current state."""
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "current_node" in data
        assert "nodes" in data
        assert "event_log" in data

    def test_update_state_valid(self, client):
        """POST /api/monitor/state with valid data should update state."""
        payload = {"node": "claude", "state": "active", "message": "Testing update"}
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] == "claude"

    def test_update_state_invalid_node(self, client):
        """POST /api/monitor/state with invalid node should return 400."""
        payload = {"node": "invalid_node", "state": "active"}
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid node" in data["error"]

    def test_update_state_no_json(self, client):
        """POST /api/monitor/state with no JSON should return 400."""
        response = client.post("/api/monitor/state")
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "No JSON data provided" in data["error"]
