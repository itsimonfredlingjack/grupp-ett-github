"""Tests for Monitor API routes."""

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app


class TestMonitorRoutes:
    """Tests for monitoring API endpoints."""

    @pytest.fixture
    def client(self) -> FlaskClient:
        """Create a test client."""
        app = create_app()
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_get_state_initial(self, client):
        """Test getting initial state."""
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert data["current_node"] is None
        assert "nodes" in data

    def test_update_state_valid(self, client):
        """Test updating state with valid data."""
        payload = {
            "node": "jira",
            "state": "active",
            "message": "Processing"
        }
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] == "jira"

    def test_update_state_invalid_node(self, client):
        """Test updating state with invalid node."""
        payload = {
            "node": "invalid",
            "state": "active"
        }
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 400

    def test_update_state_no_json(self, client):
        """Test updating state with no JSON."""
        response = client.post("/api/monitor/state")
        assert response.status_code == 400

    def test_reset(self, client):
        """Test reset endpoint."""
        # Set state first
        client.post("/api/monitor/state", json={"node": "jira", "state": "active"})

        # Reset
        response = client.post("/api/monitor/reset")
        assert response.status_code == 200

        # Verify reset
        state_response = client.get("/api/monitor/state")
        state_data = state_response.get_json()
        assert state_data["current_node"] is None

    def test_update_task(self, client):
        """Test task update endpoint."""
        payload = {
            "title": "New Task",
            "status": "running"
        }
        response = client.post("/api/monitor/task", json=payload)
        assert response.status_code == 200

        state_response = client.get("/api/monitor/state")
        task_info = state_response.get_json()["task_info"]
        assert task_info["title"] == "New Task"
        assert task_info["status"] == "running"
