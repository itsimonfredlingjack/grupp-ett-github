"""Tests for the Monitor API and WebSocket events."""

import pytest
from flask import Flask

import app as app_module  # Import module to access updated global socketio
from app import create_app
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def app():
    """Create a test application instance."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def socketio_client(app):
    """Create a SocketIO test client."""
    # Use the global socketio instance from app module, which is updated by create_app
    return app_module.socketio.test_client(app, namespace="/monitor")


class TestMonitorRoutes:
    """Tests for the Monitor REST API."""

    def test_get_state_returns_json(self, client):
        """Test that /api/monitor/state returns JSON state."""
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "nodes" in data
        assert "event_log" in data
        assert "task_info" in data

    def test_update_state_valid(self, client):
        """Test updating monitor state with valid data."""
        payload = {"node": "claude", "state": "active", "message": "Coding..."}
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        # Verify state persistence
        state_resp = client.get("/api/monitor/state")
        state_data = state_resp.get_json()
        assert state_data["current_node"] == "claude"
        assert state_data["nodes"]["claude"]["active"] is True
        assert state_data["nodes"]["claude"]["message"] == "Coding..."

    def test_update_state_invalid_node(self, client):
        """Test updating with an invalid node ID."""
        payload = {"node": "invalid_node", "state": "active"}
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid node" in data["error"]

    def test_update_state_missing_data(self, client):
        """Test updating without JSON data."""
        # Using data="" to simulate missing/empty body which get_json(silent=True) handles
        response = client.post("/api/monitor/state", data="")
        assert response.status_code == 400
        data = response.get_json()
        assert "No JSON data provided" in data["error"]

    def test_reset_monitoring(self, client):
        """Test resetting the monitoring state."""
        # First set some state
        client.post("/api/monitor/state", json={"node": "claude", "state": "active"})

        # Reset
        response = client.post("/api/monitor/reset")
        assert response.status_code == 200

        # Verify reset
        state_resp = client.get("/api/monitor/state")
        state_data = state_resp.get_json()
        assert state_data["current_node"] is None
        assert state_data["event_log"] == []

    def test_update_task(self, client):
        """Test updating task info."""
        payload = {
            "title": "Fix CI",
            "status": "running",
            "start_time": "2026-01-01T12:00:00Z"
        }
        response = client.post("/api/monitor/task", json=payload)
        assert response.status_code == 200

        # Verify task persistence
        state_resp = client.get("/api/monitor/state")
        state_data = state_resp.get_json()
        task_info = state_data["task_info"]
        assert task_info["title"] == "Fix CI"
        assert task_info["status"] == "running"
        assert task_info["start_time"] == "2026-01-01T12:00:00Z"

    def test_update_task_auto_timestamp(self, client):
        """Test that running status generates a timestamp if missing."""
        payload = {"title": "Auto Time", "status": "running"}
        client.post("/api/monitor/task", json=payload)

        state_resp = client.get("/api/monitor/state")
        state_data = state_resp.get_json()
        assert state_data["task_info"]["start_time"] is not None


class TestMonitorWebSocket:
    """Tests for the Monitor WebSocket events."""

    def test_connect_emits_initial_state(self, socketio_client):
        """Test that connecting triggers a state update."""
        assert socketio_client.is_connected(namespace="/monitor")
        received = socketio_client.get_received(namespace="/monitor")

        # Should receive at least one 'state_update' event on connect
        assert len(received) > 0
        assert received[0]["name"] == "state_update"
        data = received[0]["args"][0]
        assert "nodes" in data
        assert "event_log" in data

    def test_request_state_event(self, socketio_client):
        """Test that 'request_state' triggers an update."""
        socketio_client.emit("request_state", namespace="/monitor")
        received = socketio_client.get_received(namespace="/monitor")

        # Should find 'state_update' in response
        has_update = any(evt["name"] == "state_update" for evt in received)
        assert has_update

    def test_rest_update_broadcasts_via_websocket(self, client, socketio_client):
        """Test that REST API updates are broadcast to WebSocket clients."""
        # Clear previous events
        socketio_client.get_received(namespace="/monitor")

        # Trigger update via REST
        client.post("/api/monitor/state", json={
            "node": "github",
            "state": "active",
            "message": "Pushing..."
        })

        # Check WebSocket for broadcast
        received = socketio_client.get_received(namespace="/monitor")
        assert len(received) > 0
        last_event = received[-1]
        assert last_event["name"] == "state_update"
        data = last_event["args"][0]
        assert data["current_node"] == "github"
        assert data["nodes"]["github"]["message"] == "Pushing..."
