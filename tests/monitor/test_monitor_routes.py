"""Tests for Monitor Routes."""

import json
import pytest
from unittest.mock import MagicMock
from flask import Flask
from flask_socketio import SocketIO
from src.sejfa.monitor.monitor_service import MonitorService
from src.sejfa.monitor.monitor_routes import create_monitor_blueprint


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    monitor_service = MonitorService()
    socketio = MagicMock(spec=SocketIO)
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

    def test_update_state_valid(self, client):
        response = client.post(
            "/api/monitor/state",
            json={"node": "jira", "state": "active", "message": "working"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] == "jira"

    def test_update_state_invalid_node(self, client):
        response = client.post(
            "/api/monitor/state",
            json={"node": "invalid", "state": "active"},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_update_state_no_json(self, client):
        response = client.post("/api/monitor/state")
        assert response.status_code == 400

    def test_reset_monitoring(self, client):
        client.post(
            "/api/monitor/state",
            json={"node": "jira", "state": "active"},
        )
        response = client.post("/api/monitor/reset")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] is None

    def test_update_task(self, client):
        response = client.post(
            "/api/monitor/task",
            json={"title": "New Task", "status": "running"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["task_info"]["title"] == "New Task"
        assert data["current_state"]["task_info"]["status"] == "running"

    def test_update_task_no_json(self, client):
        response = client.post("/api/monitor/task")
        assert response.status_code == 400
