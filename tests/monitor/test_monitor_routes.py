"""Tests for Monitor Routes."""

import pytest
from flask import Flask
from flask_socketio import SocketIO

from src.sejfa.monitor.monitor_routes import (
    create_monitor_blueprint,
    init_socketio_events,
)
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    socketio = SocketIO(app)
    monitor_service = MonitorService()
    bp = create_monitor_blueprint(monitor_service, socketio)
    app.register_blueprint(bp)

    # We need to init socketio events but it requires the global socketio
    # which is injected in create_monitor_blueprint.
    # The current implementation of init_socketio_events relies on
    # the global socketio variable in monitor_routes.py.
    init_socketio_events()

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

    def test_update_state(self, client):
        payload = {"node": "jira", "state": "active", "message": "Processing"}
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["current_node"] == "jira"

    def test_update_state_invalid_node(self, client):
        payload = {"node": "invalid", "state": "active"}
        response = client.post("/api/monitor/state", json=payload)
        assert response.status_code == 400
        assert "Invalid node" in response.get_json()["error"]

    def test_update_state_no_json(self, client):
        response = client.post("/api/monitor/state")
        # Depending on flask version, get_json returns None if not json
        assert response.status_code == 400

    def test_reset_monitoring(self, client):
        # Set state first
        client.post("/api/monitor/state", json={"node": "jira"})

        response = client.post("/api/monitor/reset")
        assert response.status_code == 200
        data = response.get_json()
        assert data["current_state"]["current_node"] is None

    def test_update_task(self, client):
        payload = {"title": "New Task", "status": "running"}
        response = client.post("/api/monitor/task", json=payload)
        assert response.status_code == 200
        data = response.get_json()

        task_info = data["current_state"]["task_info"]
        assert task_info["title"] == "New Task"
        assert task_info["status"] == "running"
        assert task_info["start_time"] is not None  # Should be auto-set
