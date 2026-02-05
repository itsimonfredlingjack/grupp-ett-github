"""Integration tests for Monitor routes."""

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
    app.config["SECRET_KEY"] = "test"

    # Mock SocketIO
    socketio = SocketIO(app)

    # Create service
    service = MonitorService()

    # Register blueprint
    bp = create_monitor_blueprint(service, socketio)
    app.register_blueprint(bp)

    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestMonitorRoutes:
    """Tests for monitoring API endpoints."""

    def test_get_state(self, client):
        """Test GET /api/monitor/state."""
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "nodes" in data
        assert "task_info" in data

    def test_update_state_valid(self, client):
        """Test POST /api/monitor/state with valid data."""
        payload = {
            "node": "jira",
            "state": "active",
            "message": "Working"
        }
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] == "jira"

    def test_update_state_invalid_node(self, client):
        """Test POST /api/monitor/state with invalid node."""
        payload = {
            "node": "invalid",
            "state": "active"
        }
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid node" in data["error"]

    def test_update_state_no_json(self, client):
        """Test POST /api/monitor/state without JSON."""
        response = client.post("/api/monitor/state")
        assert response.status_code == 400

    def test_reset(self, client):
        """Test POST /api/monitor/reset."""
        # First set some state
        client.post("/api/monitor/state", json={"node": "jira", "state": "active"})

        response = client.post("/api/monitor/reset")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] is None

    def test_update_task(self, client):
        """Test POST /api/monitor/task."""
        payload = {
            "title": "My Task",
            "status": "running"
        }
        response = client.post("/api/monitor/task", json=payload)
        assert response.status_code == 200
        data = response.get_json()

        task_info = data["current_state"]["task_info"]
        assert task_info["title"] == "My Task"
        assert task_info["status"] == "running"
        # Should auto-set start time if running
        assert task_info["start_time"] is not None

    def test_update_task_no_json(self, client):
        """Test POST /api/monitor/task without JSON."""
        response = client.post("/api/monitor/task")
        assert response.status_code == 400
