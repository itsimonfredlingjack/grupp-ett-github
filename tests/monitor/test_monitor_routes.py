from unittest.mock import MagicMock

import pytest
from flask import Flask

from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def app():
    app = Flask(__name__)
    service = MonitorService()
    socketio = MagicMock()
    app.register_blueprint(create_monitor_blueprint(service, socketio))
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_state(client):
    response = client.get("/api/monitor/state")
    assert response.status_code == 200
    assert "current_node" in response.json


def test_update_state(client):
    response = client.post(
        "/api/monitor/state",
        json={"node": "claude", "state": "active", "message": "Processing"},
    )
    assert response.status_code == 200
    assert response.json["success"] is True


def test_update_state_invalid_node(client):
    response = client.post(
        "/api/monitor/state", json={"node": "invalid", "state": "active"}
    )
    assert response.status_code == 400


def test_reset_monitoring(client):
    client.post("/api/monitor/state", json={"node": "claude", "state": "active"})
    response = client.post("/api/monitor/reset")
    assert response.status_code == 200
    assert response.json["success"] is True

    state_response = client.get("/api/monitor/state")
    assert state_response.json["current_node"] is None


def test_update_task(client):
    response = client.post(
        "/api/monitor/task", json={"title": "New Task", "status": "running"}
    )
    assert response.status_code == 200
    assert response.json["success"] is True
