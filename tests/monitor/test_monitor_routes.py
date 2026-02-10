"""Unit tests for monitor routes."""

import pytest
from flask import Flask
from flask_socketio import SocketIO
from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def app_and_service():
    """Fixture providing Flask app and MonitorService."""
    app = Flask(__name__)
    service = MonitorService()
    socketio = SocketIO(app)

    # Register blueprint
    blueprint = create_monitor_blueprint(service, socketio)
    app.register_blueprint(blueprint)

    return app, service, socketio


@pytest.fixture
def client(app_and_service):
    """Fixture providing test client."""
    app, _, _ = app_and_service
    return app.test_client()


class TestMonitorRoutes:
    """Test suite for monitor API routes."""

    def test_get_state(self, client):
        """Test GET /api/monitor/state."""
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "nodes" in data
        assert "event_log" in data

    def test_update_state_valid(self, client):
        """Test POST /api/monitor/state with valid data."""
        payload = {"node": "claude", "state": "active", "message": "Processing"}
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] == "claude"

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

    def test_reset(self, client):
        """Test POST /api/monitor/reset."""
        # Set some state first
        client.post("/api/monitor/state", json={"node": "claude", "state": "active"})

        response = client.post("/api/monitor/reset")
        assert response.status_code == 200

        # Verify reset
        state_response = client.get("/api/monitor/state")
        state_data = state_response.get_json()
        assert state_data["current_node"] is None

    def test_update_task(self, client):
        """Test POST /api/monitor/task."""
        payload = {"title": "New Task", "status": "running"}
        response = client.post("/api/monitor/task", json=payload)
        assert response.status_code == 200

        state_response = client.get("/api/monitor/state")
        state = state_response.get_json()
        assert state["task_info"]["title"] == "New Task"
        assert state["task_info"]["status"] == "running"
        assert state["task_info"]["start_time"] is not None  # Auto-generated

    def test_update_task_no_json(self, client):
        """Test POST /api/monitor/task with no JSON."""
        response = client.post("/api/monitor/task")
        assert response.status_code == 400
