"""Integration tests for Monitor routes."""

from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_socketio import SocketIO

from src.sejfa.monitor.monitor_routes import (
    create_monitor_blueprint,
    init_socketio_events,
)
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def app() -> Flask:
    """Create test application."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test-secret"

    # Mock socketio
    socketio = SocketIO(app)
    monitor_service = MonitorService()

    bp = create_monitor_blueprint(monitor_service, socketio)
    app.register_blueprint(bp)

    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create test client."""
    return app.test_client()


class TestMonitorRoutes:
    """Test monitor endpoints."""

    def test_get_state(self, client: FlaskClient) -> None:
        """Test getting state."""
        response = client.get("/api/monitor/state")
        assert response.status_code == 200
        data = response.get_json()
        assert "nodes" in data
        assert "task_info" in data

    def test_update_state(self, client: FlaskClient) -> None:
        """Test updating state."""
        response = client.post(
            "/api/monitor/state",
            json={
                "node": "claude",
                "state": "active",
                "message": "Working"
            }
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["current_state"]["nodes"]["claude"]["active"] is True

    def test_update_state_invalid_node(self, client: FlaskClient) -> None:
        """Test updating with invalid node."""
        response = client.post(
            "/api/monitor/state",
            json={
                "node": "invalid_node",
                "state": "active"
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid node" in data["error"]

    def test_update_state_no_json(self, client: FlaskClient) -> None:
        """Test updating with no JSON."""
        response = client.post(
            "/api/monitor/state",
            data="not json"
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "No JSON data provided" in data["error"]

    def test_update_task(self, client: FlaskClient) -> None:
        """Test updating task."""
        response = client.post(
            "/api/monitor/task",
            json={
                "title": "New Task",
                "status": "running"
            }
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["current_state"]["task_info"]["title"] == "New Task"
        assert data["current_state"]["task_info"]["status"] == "running"
        # Check auto-assigned timestamp
        assert data["current_state"]["task_info"]["start_time"] is not None

    def test_update_task_no_json(self, client: FlaskClient) -> None:
        """Test updating task with no JSON."""
        response = client.post(
            "/api/monitor/task",
            data="not json"
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "No JSON data provided" in data["error"]

    def test_reset(self, client: FlaskClient) -> None:
        """Test reset."""
        # Set some state first
        client.post("/api/monitor/state", json={"node": "claude", "state": "active"})

        response = client.post("/api/monitor/reset")
        assert response.status_code == 200

        # Verify reset
        state_resp = client.get("/api/monitor/state")
        state = state_resp.get_json()
        assert state["nodes"]["claude"]["active"] is False

    def test_socketio_events(self, app: Flask) -> None:
        """Test SocketIO event handlers initialization."""
        # This just verifies the function runs without error
        # Mock socketio to avoid actual connection attempts in unit test
        with patch("src.sejfa.monitor.monitor_routes.socketio") as mock_socketio:
            init_socketio_events()
            # Verify decorators were called
            assert mock_socketio.on.call_count >= 3

    def test_server_error_handling(self, client: FlaskClient) -> None:
        """Test server error handling in endpoints."""
        with patch("src.sejfa.monitor.monitor_routes.monitor_service") as mock_service:
            mock_service.get_state.side_effect = Exception("Simulated error")

            response = client.get("/api/monitor/state")
            assert response.status_code == 500
            data = response.get_json()
            assert data["success"] is False
            assert "Simulated error" in data["error"]
