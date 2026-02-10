from unittest.mock import MagicMock

import pytest
from flask import Flask, json
from flask_socketio import SocketIO

from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test"
    # Mock SocketIO to avoid async complications in simple tests
    socketio = MagicMock(spec=SocketIO)
    service = MonitorService()
    bp = create_monitor_blueprint(service, socketio)
    app.register_blueprint(bp)
    app.monitor_service = service
    app.socketio = socketio
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_state(client):
    response = client.get("/api/monitor/state")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "nodes" in data
    assert "current_node" in data


def test_update_state_success(client, app):
    payload = {"node": "claude", "state": "active", "message": "Thinking..."}
    response = client.post("/api/monitor/state", json=payload)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True

    # Verify service updated
    assert app.monitor_service.current_node == "claude"
    # Verify socket emission
    app.socketio.emit.assert_called()


def test_update_state_invalid_node(client):
    payload = {"node": "invalid_node", "state": "active"}
    response = client.post("/api/monitor/state", json=payload)

    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False
    assert "Invalid node" in data["error"]


def test_update_state_no_json(client):
    response = client.post("/api/monitor/state")
    # Depending on how flask handles no json, usually 400 or 415,
    # but the code explicit check `if not data` returns 400.
    # However, client.post without json might send empty body but wrong content-type.
    # Let's force None data by sending empty dict as json which makes
    # `request.get_json()` return {} (truthy?)
    # Actually `client.post` with no data might result in None from get_json
    # if silent=True not used?
    # The code uses `data = request.get_json()` without silent=True,
    # so it throws 400 if parsing fails.
    # The code checks `if not data`, so empty dict/None triggers 400.
    assert response.status_code == 400


def test_update_task_success(client, app):
    payload = {"title": "Fix bug", "status": "running"}
    response = client.post("/api/monitor/task", json=payload)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True

    task_info = app.monitor_service.get_task_info()
    assert task_info["title"] == "Fix bug"
    assert task_info["status"] == "running"
    assert task_info["start_time"] is not None  # Auto-generated


def test_reset_monitoring(client, app):
    # Set some state first
    app.monitor_service.update_node("claude", "active")

    response = client.post("/api/monitor/reset")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True

    assert app.monitor_service.current_node is None
