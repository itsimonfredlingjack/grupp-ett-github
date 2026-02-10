import pytest
from flask import Flask
from flask_socketio import SocketIO
from unittest.mock import MagicMock, patch
from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app

@pytest.fixture
def socketio():
    return MagicMock(spec=SocketIO)

@pytest.fixture
def monitor_service():
    return MonitorService()

@pytest.fixture
def client(app, monitor_service, socketio):
    blueprint = create_monitor_blueprint(monitor_service, socketio)
    app.register_blueprint(blueprint)
    return app.test_client()

def test_get_state(client):
    response = client.get("/api/monitor/state")
    assert response.status_code == 200
    data = response.get_json()
    assert "current_node" in data
    assert "nodes" in data

def test_update_state_valid(client, socketio):
    response = client.post("/api/monitor/state", json={
        "node": "claude",
        "state": "active",
        "message": "testing"
    })
    assert response.status_code == 200
    assert socketio.emit.called

def test_update_state_invalid_node(client):
    response = client.post("/api/monitor/state", json={
        "node": "invalid",
        "state": "active"
    })
    assert response.status_code == 400

def test_update_state_no_json(client):
    # Flask test client content_type defaults appropriately but let's send empty body
    response = client.post("/api/monitor/state")
    assert response.status_code == 400

def test_reset(client, socketio):
    response = client.post("/api/monitor/reset")
    assert response.status_code == 200
    assert socketio.emit.called

def test_update_task(client, socketio):
    response = client.post("/api/monitor/task", json={
        "title": "New Task",
        "status": "running"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["current_state"]["task_info"]["title"] == "New Task"
