import pytest
from flask import Flask
from unittest.mock import MagicMock
from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService

@pytest.fixture
def monitor_service():
    return MonitorService()

@pytest.fixture
def socketio():
    return MagicMock()

@pytest.fixture
def client(monitor_service, socketio):
    app = Flask(__name__)
    app.register_blueprint(create_monitor_blueprint(monitor_service, socketio))
    app.config["TESTING"] = True
    return app.test_client()

class TestMonitorRoutes:
    def test_update_state_valid(self, client, monitor_service):
        response = client.post("/api/monitor/state", json={
            "node": "claude",
            "state": "active",
            "message": "Thinking"
        })
        assert response.status_code == 200
        assert response.json["success"] is True
        assert monitor_service.current_node == "claude"

    def test_update_state_invalid_node(self, client):
        response = client.post("/api/monitor/state", json={
            "node": "invalid",
            "state": "active"
        })
        assert response.status_code == 400
        assert response.json["success"] is False

    def test_update_state_no_json(self, client):
        response = client.post("/api/monitor/state")
        assert response.status_code == 400

    def test_get_state(self, client, monitor_service):
        monitor_service.update_node("jira", "active")
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        assert response.json["current_node"] == "jira"

    def test_reset_monitoring(self, client, monitor_service):
        monitor_service.update_node("claude", "active")
        response = client.post("/api/monitor/reset")
        assert response.status_code == 200
        assert response.json["success"] is True
        assert monitor_service.current_node is None

    def test_update_task(self, client, monitor_service):
        response = client.post("/api/monitor/task", json={
            "title": "Fix bug",
            "status": "running"
        })
        assert response.status_code == 200
        assert monitor_service.task_info["title"] == "Fix bug"
        assert monitor_service.task_info["status"] == "running"
        assert monitor_service.task_info["start_time"] is not None  # Auto-generated

    def test_update_task_no_json(self, client):
        response = client.post("/api/monitor/task")
        assert response.status_code == 400
