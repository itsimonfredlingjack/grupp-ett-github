"""Integration tests for Monitor routes."""

import pytest
from flask import Flask

from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorRoutes:
    """Tests for monitor API endpoints."""

    @pytest.fixture
    def app(self):
        """Create a Flask app with monitor blueprint."""
        app = Flask(__name__)
        app.config["TESTING"] = True

        # Mock SocketIO
        class MockSocketIO:
            def emit(self, event, data, namespace=None, skip_sid=None):
                pass

            def on(self, event, namespace=None):
                def decorator(f):
                    return f

                return decorator

        socketio = MockSocketIO()
        service = MonitorService()

        blueprint = create_monitor_blueprint(service, socketio)
        app.register_blueprint(blueprint)

        return app

    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return app.test_client()

    def test_get_state(self, client):
        """Test GET /state endpoint."""
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "nodes" in data
        assert "current_node" in data

    def test_update_state_valid(self, client):
        """Test POST /state with valid data."""
        payload = {"node": "claude", "state": "active", "message": "Working"}
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] == "claude"

    def test_update_state_invalid_node(self, client):
        """Test POST /state with invalid node."""
        payload = {"node": "invalid", "state": "active"}
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid node" in data["error"]

    def test_update_state_no_json(self, client):
        """Test POST /state without JSON."""
        response = client.post("/api/monitor/state")
        assert response.status_code == 400

    def test_reset_monitoring(self, client):
        """Test POST /reset endpoint."""
        # First set some state
        client.post("/api/monitor/state", json={"node": "claude", "state": "active"})

        response = client.post("/api/monitor/reset")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] is None

    def test_update_task(self, client):
        """Test POST /task endpoint."""
        payload = {"title": "New Task", "status": "running"}
        response = client.post("/api/monitor/task", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["task_info"]["title"] == "New Task"
        assert data["current_state"]["task_info"]["status"] == "running"

    def test_update_task_no_json(self, client):
        """Test POST /task without JSON."""
        response = client.post("/api/monitor/task")
        assert response.status_code == 400
