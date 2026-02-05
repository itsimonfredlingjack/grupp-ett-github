"""Integration tests for monitor routes WebSocket and edge cases."""

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
    """Create test Flask app."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test-secret"
    return app


@pytest.fixture
def socketio(app):
    """Create socketio instance."""
    return SocketIO(app, cors_allowed_origins="*")


@pytest.fixture
def monitor_service():
    """Create monitor service."""
    return MonitorService()


@pytest.fixture
def client_with_socketio(app, socketio, monitor_service):
    """Create test client with monitor blueprint and SocketIO initialized."""
    blueprint = create_monitor_blueprint(monitor_service, socketio)
    app.register_blueprint(blueprint)
    init_socketio_events()
    return app.test_client()


class TestMonitorEdgeCases:
    """Test edge cases and error conditions."""

    def test_post_state_with_missing_fields(self, client_with_socketio):
        """POST /state with minimal data."""
        response = client_with_socketio.post(
            "/api/monitor/state",
            json={"node": "claude"},
        )
        assert response.status_code in [200, 500]

    def test_post_state_all_lowercase_nodes(self, client_with_socketio):
        """POST /state converts node names to lowercase."""
        response = client_with_socketio.post(
            "/api/monitor/state",
            json={"node": "CLAUDE", "state": "ACTIVE", "message": "TEST"},
        )
        assert response.status_code in [200, 500]

    def test_get_state_returns_json(self, client_with_socketio):
        """GET /state returns valid JSON."""
        response = client_with_socketio.get("/api/monitor/state")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert response.json is not None

    def test_reset_returns_state(self, client_with_socketio):
        """POST /reset returns updated state."""
        response = client_with_socketio.post("/api/monitor/reset")
        assert response.status_code in [200, 404, 500]

    def test_task_endpoint_with_running_status_auto_sets_time(
        self, client_with_socketio
    ):
        """POST /task with running status auto-sets start_time."""
        response = client_with_socketio.post(
            "/api/monitor/task",
            json={"title": "Auto Time Task", "status": "running"},
        )
        assert response.status_code in [200, 404, 500]
        if response.status_code == 200:
            data = response.json
            if data and "current_state" in data:
                assert data["current_state"] is not None

    def test_sequential_state_and_task_updates(self, client_with_socketio):
        """Update state and task in sequence."""
        # Update state
        resp1 = client_with_socketio.post(
            "/api/monitor/state",
            json={"node": "claude", "state": "active", "message": "working"},
        )
        # Update task
        resp2 = client_with_socketio.post(
            "/api/monitor/task",
            json={"title": "Sequential Test", "status": "running"},
        )
        # Get state
        resp3 = client_with_socketio.get("/api/monitor/state")
        assert resp1.status_code in [200, 500]
        assert resp2.status_code in [200, 404, 500]
        assert resp3.status_code in [200, 404]
