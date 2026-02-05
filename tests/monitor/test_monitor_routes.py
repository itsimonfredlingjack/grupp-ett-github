"""Tests for Monitor Routes."""

import pytest
from flask import Flask
from flask_socketio import SocketIO
from src.sejfa.monitor.monitor_service import MonitorService
from src.sejfa.monitor.monitor_routes import create_monitor_blueprint

@pytest.fixture
def app():
    """Create a test Flask application with monitor blueprint."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test"

    socketio = SocketIO(app)
    monitor_service = MonitorService()

    # Pre-populate some data
    monitor_service.update_node("claude", "active", "Test message")
    monitor_service.set_task_info(title="Test Task", status="running")

    bp = create_monitor_blueprint(monitor_service, socketio)
    app.register_blueprint(bp)

    return app

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

def test_get_state(client):
    """Test getting status JSON."""
    response = client.get("/api/monitor/state")
    assert response.status_code == 200
    data = response.get_json()
    assert data["current_node"] == "claude"
    assert data["task_info"]["title"] == "Test Task"

def test_update_state(client):
    """Test updating status via API."""
    response = client.post("/api/monitor/state", json={
        "node": "github",
        "state": "active",
        "message": "Pushing code"
    })
    assert response.status_code == 200

    # Verify update
    response = client.get("/api/monitor/state")
    data = response.get_json()
    assert data["current_node"] == "github"

def test_update_state_invalid_node(client):
    """Test updating with invalid node."""
    response = client.post("/api/monitor/state", json={
        "node": "invalid",
        "state": "active"
    })
    assert response.status_code == 400

def test_update_task(client):
    """Test updating task info."""
    response = client.post("/api/monitor/task", json={
        "title": "New Task",
        "status": "completed"
    })
    assert response.status_code == 200

    # Verify update
    response = client.get("/api/monitor/state")
    data = response.get_json()
    assert data["task_info"]["title"] == "New Task"
    assert data["task_info"]["status"] == "completed"

def test_reset(client):
    """Test reset endpoint."""
    response = client.post("/api/monitor/reset")
    assert response.status_code == 200

    # Verify reset
    response = client.get("/api/monitor/state")
    data = response.get_json()
    assert data["current_node"] is None
