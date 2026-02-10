"""Tests for Monitor Routes."""

import pytest
from app import create_app
from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorRoutes:
    """Tests for monitoring API endpoints."""

    @pytest.fixture
    def app(self):
        """Create Flask app for testing."""
        app = create_app()
        app.config.update({
            "TESTING": True,
        })
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    def test_get_state(self, client):
        """Test GET /api/monitor/state."""
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "current_node" in data
        assert "nodes" in data
        assert "event_log" in data

    def test_update_state_valid(self, client):
        """Test POST /api/monitor/state with valid data."""
        payload = {
            "node": "claude",
            "state": "active",
            "message": "Coding..."
        }
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] == "claude"

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
        """Test POST /api/monitor/state with no JSON."""
        response = client.post("/api/monitor/state")
        assert response.status_code == 400

    def test_reset_monitoring(self, client):
        """Test POST /api/monitor/reset."""
        # First set some state
        client.post("/api/monitor/state", json={"node": "claude", "state": "active"})

        response = client.post("/api/monitor/reset")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] is None

    def test_update_task(self, client):
        """Test POST /api/monitor/task."""
        payload = {
            "title": "Fix Bugs",
            "status": "running"
        }
        response = client.post("/api/monitor/task", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["task_info"]["title"] == "Fix Bugs"
        # Check that start_time was automatically set for running status
        assert data["current_state"]["task_info"]["start_time"] is not None

    def test_update_task_no_json(self, client):
        """Test POST /api/monitor/task with no JSON."""
        response = client.post("/api/monitor/task")
        assert response.status_code == 400
