"""Tests for Monitor Routes."""

import pytest
from flask import Flask
from unittest.mock import MagicMock
from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorRoutes:
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.config["TESTING"] = True

        # Mock dependencies
        self.service = MonitorService()
        self.socketio = MagicMock()

        blueprint = create_monitor_blueprint(self.service, self.socketio)
        app.register_blueprint(blueprint)

        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_get_state(self, client):
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "nodes" in data
        assert "event_log" in data

    def test_update_state_valid(self, client):
        payload = {
            "node": "claude",
            "state": "active",
            "message": "Thinking..."
        }
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 200
        assert response.get_json()["success"] is True

        # Verify service was updated
        assert self.service.nodes["claude"].active is True
        # Verify socket emission
        self.socketio.emit.assert_called()

    def test_update_state_invalid_node(self, client):
        payload = {
            "node": "invalid_node",
            "state": "active"
        }
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 400
        assert "Invalid node" in response.get_json()["error"]

    def test_update_state_no_json(self, client):
        response = client.post("/api/monitor/state")
        assert response.status_code == 400  # Or 415/500 depending on flask version, but code says 400

    def test_reset_monitoring(self, client):
        # Set some state first
        self.service.update_node("claude", "active", "msg")

        response = client.post("/api/monitor/reset")
        assert response.status_code == 200

        # Verify reset
        assert self.service.nodes["claude"].active is False
        self.socketio.emit.assert_called()

    def test_update_task(self, client):
        payload = {
            "title": "Fix CI",
            "status": "running"
        }
        response = client.post("/api/monitor/task", json=payload)
        assert response.status_code == 200

        info = self.service.get_task_info()
        assert info["title"] == "Fix CI"
        assert info["status"] == "running"
        assert info["start_time"] is not None  # Auto-generated

    def test_update_task_no_json(self, client):
        response = client.post("/api/monitor/task")
        assert response.status_code == 400
