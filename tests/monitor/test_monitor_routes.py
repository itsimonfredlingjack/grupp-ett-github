from unittest.mock import MagicMock

import pytest
from flask import Flask

from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def monitor_service():
    return MonitorService()


@pytest.fixture
def mock_socketio():
    return MagicMock()


@pytest.fixture
def app(monitor_service, mock_socketio):
    app = Flask(__name__)
    blueprint = create_monitor_blueprint(monitor_service, mock_socketio)
    app.register_blueprint(blueprint)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestMonitorRoutes:
    def test_get_state(self, client, monitor_service):
        monitor_service.update_node("claude", "active", "Test")
        response = client.get("/api/monitor/state")

        assert response.status_code == 200
        data = response.get_json()
        assert data["current_node"] == "claude"
        assert data["nodes"]["claude"]["active"] is True

    def test_update_state_valid(self, client, mock_socketio):
        payload = {"node": "claude", "state": "active", "message": "Working"}
        response = client.post("/api/monitor/state", json=payload)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] == "claude"

        # Verify SocketIO emit
        mock_socketio.emit.assert_called_with(
            "state_update", data["current_state"], namespace="/monitor", skip_sid=None
        )

    def test_update_state_invalid_node(self, client):
        payload = {"node": "invalid_node", "state": "active"}
        response = client.post("/api/monitor/state", json=payload)

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid node" in data["error"]

    def test_update_state_no_json(self, client):
        response = client.post("/api/monitor/state")
        assert response.status_code == 400

    def test_reset_monitoring(self, client, monitor_service, mock_socketio):
        monitor_service.update_node("claude", "active")

        response = client.post("/api/monitor/reset")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert monitor_service.current_node is None

        mock_socketio.emit.assert_called()

    def test_update_task(self, client, monitor_service, mock_socketio):
        payload = {"title": "New Task", "status": "running"}
        response = client.post("/api/monitor/task", json=payload)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert monitor_service.task_info["title"] == "New Task"
        assert monitor_service.task_info["status"] == "running"
        # Check auto-generated timestamp
        assert monitor_service.task_info["start_time"] is not None

        mock_socketio.emit.assert_called()

    def test_update_task_no_json(self, client):
        response = client.post("/api/monitor/task")
        assert response.status_code == 400

    def test_server_error_handling(self, client, monitor_service):
        # Mock a method to raise exception
        monitor_service.get_state = MagicMock(side_effect=Exception("Database error"))

        response = client.get("/api/monitor/state")
        assert response.status_code == 500
        data = response.get_json()
        assert data["success"] is False
        assert "Server error" in data["error"]
