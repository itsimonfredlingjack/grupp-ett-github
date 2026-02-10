"""Tests for Monitor Routes."""

import json
import pytest
import app as app_module
from app import create_app
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,  # Disable CSRF for easier testing
        }
    )
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def socket_client(app):
    """Create socketio test client."""
    # Access socketio from the module to get the updated instance
    return app_module.socketio.test_client(app, namespace="/monitor")


class TestMonitorRoutes:
    """Test cases for monitor API endpoints."""

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer dev-monitor-key"}

    def test_get_state(self, client):
        """Test GET /api/monitor/state."""
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "nodes" in data
        assert "event_log" in data

    def test_update_state_success(self, client, auth_headers):
        """Test POST /api/monitor/state with valid data."""
        payload = {"node": "claude", "state": "active", "message": "Processing"}
        response = client.post("/api/monitor/state", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] == "claude"

    def test_update_state_unauthorized(self, client):
        """Test POST /api/monitor/state without auth."""
        response = client.post("/api/monitor/state", json={"node": "claude"})
        assert response.status_code == 401

    def test_update_state_invalid_node(self, client, auth_headers):
        """Test POST /api/monitor/state with invalid node."""
        payload = {"node": "invalid", "state": "active"}
        response = client.post("/api/monitor/state", json=payload, headers=auth_headers)
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid node" in data["error"]

    def test_update_state_no_json(self, client, auth_headers):
        """Test POST /api/monitor/state without JSON."""
        response = client.post("/api/monitor/state", headers=auth_headers)
        assert response.status_code == 400

    def test_reset_monitoring(self, client, auth_headers):
        """Test POST /api/monitor/reset."""
        # Set some state first
        client.post(
            "/api/monitor/state",
            json={"node": "jira", "state": "active"},
            headers=auth_headers,
        )

        response = client.post("/api/monitor/reset", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        # Verify state is cleared
        state_resp = client.get("/api/monitor/state")
        state_data = state_resp.get_json()
        assert state_data["current_node"] is None

    def test_update_task(self, client, auth_headers):
        """Test POST /api/monitor/task."""
        payload = {"title": "My Task", "status": "running"}
        response = client.post("/api/monitor/task", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["task_info"]["title"] == "My Task"
        assert data["current_state"]["task_info"]["status"] == "running"
        assert (
            data["current_state"]["task_info"]["start_time"] is not None
        )  # Auto-generated

    def test_update_task_no_json(self, client, auth_headers):
        """Test POST /api/monitor/task without JSON."""
        response = client.post("/api/monitor/task", headers=auth_headers)
        assert response.status_code == 400

    def test_socketio_connection(self, socket_client):
        """Test WebSocket connection receives initial state."""
        assert socket_client.is_connected(namespace="/monitor")
        received = socket_client.get_received(namespace="/monitor")
        # Expect at least one 'state_update' event on connect
        assert any(e["name"] == "state_update" for e in received)
