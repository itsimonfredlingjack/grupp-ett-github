"""Tests for Monitor Routes."""

import json
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from src.sejfa.monitor.monitor_routes import create_monitor_blueprint, init_socketio_events
from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorRoutes:
    @pytest.fixture
    def mock_socketio(self):
        return MagicMock()

    @pytest.fixture
    def monitor_service(self):
        return MonitorService()

    @pytest.fixture
    def app(self, monitor_service, mock_socketio):
        app = Flask(__name__)
        blueprint = create_monitor_blueprint(monitor_service, mock_socketio)
        app.register_blueprint(blueprint)
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_get_state(self, client):
        """Test GET /api/monitor/state."""
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "current_node" in data
        assert "nodes" in data

    def test_update_state_valid(self, client, mock_socketio):
        """Test POST /api/monitor/state with valid data."""
        payload = {"node": "claude", "state": "active", "message": "Test"}
        response = client.post("/api/monitor/state", json=payload)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["current_state"]["current_node"] == "claude"

        # Verify socket emission
        mock_socketio.emit.assert_called_with(
            "state_update",
            data["current_state"],
            namespace="/monitor",
            skip_sid=None
        )

    def test_update_state_invalid_node(self, client):
        """Test POST /api/monitor/state with invalid node."""
        payload = {"node": "invalid", "state": "active"}
        response = client.post("/api/monitor/state", json=payload)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False
        assert "Invalid node" in data["error"]

    def test_update_state_no_json(self, client):
        """Test POST /api/monitor/state with no JSON."""
        response = client.post("/api/monitor/state")
        assert response.status_code == 400

    def test_reset_monitoring(self, client, mock_socketio):
        """Test POST /api/monitor/reset."""
        response = client.post("/api/monitor/reset")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["message"] == "Monitoring state reset"

        mock_socketio.emit.assert_called()

    def test_update_task(self, client, mock_socketio):
        """Test POST /api/monitor/task."""
        payload = {"title": "New Task", "status": "running"}
        response = client.post("/api/monitor/task", json=payload)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["current_state"]["task_info"]["title"] == "New Task"
        assert data["current_state"]["task_info"]["status"] == "running"
        assert data["current_state"]["task_info"]["start_time"] is not None # Should be set automatically

    def test_update_task_no_json(self, client):
        """Test POST /api/monitor/task with no JSON."""
        response = client.post("/api/monitor/task")
        assert response.status_code == 400

    def test_init_socketio_events(self, mock_socketio, monitor_service):
        """Test initialization of socket events."""
        # This function uses global variables, so we need to ensure they are set
        # create_monitor_blueprint sets them.
        create_monitor_blueprint(monitor_service, mock_socketio)
        init_socketio_events()

        assert mock_socketio.on.call_count >= 1
        # Verify connect handler is registered
        mock_socketio.on.assert_any_call("connect", namespace="/monitor")

    def test_server_error_handling(self, client, monitor_service):
        """Test error handling when service raises exception."""
        # Mock update_node to raise exception
        monitor_service.update_node = MagicMock(side_effect=Exception("Test Error"))

        payload = {"node": "claude", "state": "active"}
        response = client.post("/api/monitor/state", json=payload)

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data["success"] is False
        assert "Test Error" in data["error"]
