"""Tests for Monitor Routes."""

import pytest
from flask import Flask
from flask_socketio import SocketIO

from src.sejfa.monitor.monitor_routes import (
    create_monitor_blueprint,
    init_socketio_events,
)
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def app():
    """Create test app."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    socketio = SocketIO(app)
    service = MonitorService()

    # Initialize blueprint
    bp = create_monitor_blueprint(service, socketio)
    app.register_blueprint(bp)

    # Init events (though hard to test without socketio client in this fixture style)
    init_socketio_events()

    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestMonitorRoutes:
    """Test suite for monitor endpoints."""

    def test_get_state(self, client):
        """Test GET /state."""
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "nodes" in data
        assert "event_log" in data

    def test_update_state_valid(self, client):
        """Test POST /state with valid data."""
        response = client.post("/api/monitor/state", json={
            "node": "claude",
            "state": "active",
            "message": "Working"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"]
        assert data["current_state"]["current_node"] == "claude"

    def test_update_state_invalid_node(self, client):
        """Test POST /state with invalid node."""
        response = client.post("/api/monitor/state", json={
            "node": "invalid",
            "state": "active"
        })
        assert response.status_code == 400

    def test_update_state_no_json(self, client):
        """Test POST /state with no JSON."""
        response = client.post("/api/monitor/state")
        assert response.status_code == 400

    def test_reset(self, client):
        """Test POST /reset."""
        # Set state first
        client.post("/api/monitor/state", json={"node": "claude"})

        response = client.post("/api/monitor/reset")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"]
        assert data["current_state"]["current_node"] is None

    def test_update_task(self, client):
        """Test POST /task."""
        response = client.post("/api/monitor/task", json={
            "title": "New Task",
            "status": "running"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data["current_state"]["task_info"]["title"] == "New Task"
        assert data["current_state"]["task_info"]["status"] == "running"
        assert data["current_state"]["task_info"]["start_time"]  # Should be auto-set

    def test_update_task_no_json(self, client):
        """Test POST /task with no JSON."""
        response = client.post("/api/monitor/task")
        assert response.status_code == 400
