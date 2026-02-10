"""
Integration tests for Monitor API routes.
"""

from unittest.mock import MagicMock

import pytest
from flask import Flask

from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorRoutes:
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        service = MonitorService()
        socketio = MagicMock()

        blueprint = create_monitor_blueprint(service, socketio)
        app.register_blueprint(blueprint)

        # Expose service for tests
        app.monitor_service = service
        app.socketio = socketio
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_get_state(self, client):
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "current_node" in data
        assert "nodes" in data

    def test_update_state_valid(self, client, app):
        payload = {
            "node": "claude",
            "state": "active",
            "message": "Processing..."
        }
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 200
        assert response.get_json()["success"] is True

        # Verify service state
        assert app.monitor_service.current_node == "claude"
        # Verify socket emit
        app.socketio.emit.assert_called_with(
            "state_update",
            app.monitor_service.get_state(),
            namespace="/monitor",
            skip_sid=None
        )

    def test_update_state_invalid_node(self, client):
        payload = {"node": "invalid", "state": "active"}
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 400
        assert response.get_json()["success"] is False

    def test_update_state_no_data(self, client):
        # Empty dict acts as data but content is checked
        response = client.post("/api/monitor/state", json={})

        # Send None (no json body)
        # get_json() returns None if mimetype wrong or empty dict if {} sent.
        response = client.post("/api/monitor/state")

        # If no data, it returns 400.
        assert response.status_code == 400

    def test_reset_monitoring(self, client, app):
        # Set some state first
        client.post("/api/monitor/state", json={"node": "jira", "state": "active"})

        response = client.post("/api/monitor/reset")
        assert response.status_code == 200
        assert response.get_json()["success"] is True

        assert app.monitor_service.current_node is None

    def test_update_task(self, client, app):
        payload = {
            "title": "My Task",
            "status": "running"
        }
        response = client.post("/api/monitor/task", json=payload)
        assert response.status_code == 200

        info = app.monitor_service.get_task_info()
        assert info["title"] == "My Task"
        assert info["status"] == "running"
        assert info["start_time"] is not None  # Auto-generated

    def test_update_task_no_data(self, client):
        response = client.post("/api/monitor/task")
        assert response.status_code == 400
