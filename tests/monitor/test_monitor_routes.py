"""Tests for Monitor Routes."""

import pytest
from flask import Flask
from flask_socketio import SocketIO

from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    socketio = SocketIO(app)
    monitor_service = MonitorService()

    blueprint = create_monitor_blueprint(monitor_service, socketio)
    app.register_blueprint(blueprint)

    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestMonitorRoutes:
    def test_get_state(self, client):
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "current_node" in data
        assert "nodes" in data

    def test_update_state_valid(self, client):
        response = client.post(
            "/api/monitor/state",
            json={"node": "jira", "state": "active", "message": "Testing"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] == "jira"

    def test_update_state_invalid_node(self, client):
        response = client.post(
            "/api/monitor/state", json={"node": "invalid", "state": "active"}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_update_state_no_json(self, client):
        response = client.post("/api/monitor/state")
        assert response.status_code == 400

    def test_reset(self, client):
        # Set some state first
        client.post("/api/monitor/state", json={"node": "jira"})

        response = client.post("/api/monitor/reset")
        assert response.status_code == 200

        # Verify reset
        state_resp = client.get("/api/monitor/state")
        assert state_resp.get_json()["current_node"] is None

    def test_update_task(self, client):
        response = client.post(
            "/api/monitor/task", json={"title": "New Task", "status": "running"}
        )
        assert response.status_code == 200

        state_resp = client.get("/api/monitor/state")
        task_info = state_resp.get_json()["task_info"]
        assert task_info["title"] == "New Task"
        assert task_info["status"] == "running"
        assert task_info["start_time"] is not None  # Auto-set

    def test_update_task_no_json(self, client):
        response = client.post("/api/monitor/task")
        assert response.status_code == 400
