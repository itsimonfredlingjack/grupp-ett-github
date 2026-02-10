"""Tests for the Monitor Routes."""

import json
import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from src.sejfa.monitor.monitor_service import MonitorService
from src.sejfa.monitor.monitor_routes import (
    create_monitor_blueprint,
    init_socketio_events,
)


class MockSocketIO:
    """Mock for Flask-SocketIO."""

    def __init__(self):
        self.emit = MagicMock()
        self.on_handlers = {}

    def on(self, event, namespace=None):
        def decorator(f):
            self.on_handlers[(event, namespace)] = f
            return f

        return decorator


@pytest.fixture
def monitor_service():
    """Fixture for MonitorService."""
    return MonitorService()


@pytest.fixture
def mock_socketio():
    """Fixture for MockSocketIO."""
    return MockSocketIO()


@pytest.fixture
def client(monitor_service, mock_socketio):
    """Fixture for Flask test client with monitor blueprint."""
    app = Flask(__name__)
    blueprint = create_monitor_blueprint(monitor_service, mock_socketio)
    app.register_blueprint(blueprint)

    # Initialize events to test them too (though difficult without actual socketio context)
    # create_monitor_blueprint sets global socketio in module, so init_socketio_events should use it
    init_socketio_events()

    with app.test_client() as client:
        yield client


class TestMonitorRoutes:
    """Tests for monitor API routes."""

    def test_update_state_success(self, client, monitor_service, mock_socketio):
        """Test successful state update."""
        response = client.post(
            "/api/monitor/state",
            json={"node": "jira", "state": "active", "message": "Fetching issues"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        # Verify service update
        state = monitor_service.get_state()
        assert state["current_node"] == "jira"

        # Verify socket emission
        mock_socketio.emit.assert_called_with(
            "state_update", state, namespace="/monitor", skip_sid=None
        )

    def test_update_state_invalid_node(self, client):
        """Test state update with invalid node."""
        response = client.post(
            "/api/monitor/state", json={"node": "invalid", "state": "active"}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_update_state_no_data(self, client):
        """Test state update with no data."""
        response = client.post("/api/monitor/state", content_type="application/json")
        assert response.status_code == 400

    def test_get_state(self, client, monitor_service):
        """Test getting current state."""
        monitor_service.update_node("jira", "active", "Test")

        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert data["current_node"] == "jira"

    def test_reset_monitoring(self, client, monitor_service, mock_socketio):
        """Test resetting monitoring state."""
        monitor_service.update_node("jira", "active", "Test")

        response = client.post("/api/monitor/reset")
        assert response.status_code == 200

        state = monitor_service.get_state()
        assert state["current_node"] is None

        # Verify socket emission
        mock_socketio.emit.assert_called_with(
            "state_update", state, namespace="/monitor", skip_sid=None
        )

    def test_update_task(self, client, monitor_service, mock_socketio):
        """Test updating task info."""
        response = client.post(
            "/api/monitor/task", json={"title": "New Task", "status": "running"}
        )
        assert response.status_code == 200

        info = monitor_service.get_task_info()
        assert info["title"] == "New Task"
        assert info["status"] == "running"
        assert (
            info["start_time"] is not None
        )  # Should be set automatically if not provided

    def test_update_task_no_data(self, client):
        """Test update task with no data."""
        response = client.post("/api/monitor/task", content_type="application/json")
        assert response.status_code == 400

    def test_socketio_connect(self, client, mock_socketio, monitor_service):
        """Test socketio connect handler."""
        # Patch the emit function in monitor_routes
        with patch("src.sejfa.monitor.monitor_routes.emit") as mock_emit:
            handler = mock_socketio.on_handlers.get(("connect", "/monitor"))
            assert handler is not None

            # Simulate connection
            handler()

            # Verify initial state emission via flask_socketio.emit
            mock_emit.assert_called_with("state_update", monitor_service.get_state())
