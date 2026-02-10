"""Tests for Monitor Routes."""

import pytest
from flask import Flask
from flask_socketio import SocketIO
from src.sejfa.monitor.monitor_service import MonitorService
from src.sejfa.monitor.monitor_routes import create_monitor_blueprint


class TestMonitorRoutes:
    """Tests for monitoring routes."""

    @pytest.fixture
    def app(self):
        """Create and configure a new app instance for each test."""
        app = Flask(__name__)
        app.config["TESTING"] = True

        socketio = SocketIO(app)
        service = MonitorService()

        blueprint = create_monitor_blueprint(service, socketio)
        app.register_blueprint(blueprint)

        return app

    @pytest.fixture
    def client(self, app):
        """A test client for the app."""
        return app.test_client()

    def test_get_state(self, client):
        """Test GET /api/monitor/state."""
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "current_node" in data
        assert "nodes" in data

    def test_update_state_success(self, client):
        """Test POST /api/monitor/state with valid data."""
        payload = {"node": "jira", "state": "active", "message": "Processing ticket"}
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] == "jira"

    def test_update_state_invalid_node(self, client):
        """Test POST /api/monitor/state with invalid node."""
        payload = {"node": "invalid_node", "state": "active"}
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid node" in data["error"]

    def test_update_state_no_json(self, client):
        """Test POST /api/monitor/state without JSON."""
        response = client.post("/api/monitor/state")
        assert response.status_code == 400

    def test_reset_monitoring(self, client):
        """Test POST /api/monitor/reset."""
        # First set some state
        client.post("/api/monitor/state", json={"node": "jira", "state": "active"})

        # Then reset
        response = client.post("/api/monitor/reset")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] is None

    def test_update_task(self, client):
        """Test POST /api/monitor/task."""
        payload = {"title": "New Task", "status": "running"}
        response = client.post("/api/monitor/task", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["task_info"]["title"] == "New Task"
        assert data["current_state"]["task_info"]["status"] == "running"
        # Check auto-generated timestamp
        assert data["current_state"]["task_info"]["start_time"] is not None

    def test_update_task_no_json(self, client):
        """Test POST /api/monitor/task without JSON."""
        response = client.post("/api/monitor/task")
        assert response.status_code == 400
