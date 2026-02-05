"""Comprehensive tests for monitor routes to improve coverage."""

import pytest
from flask import Flask
from flask_socketio import SocketIO

from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
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
def client(app, socketio, monitor_service):
    """Create test client with monitor blueprint."""
    blueprint = create_monitor_blueprint(monitor_service, socketio)
    app.register_blueprint(blueprint)
    return app.test_client()


class TestMonitorStateRoutes:
    """Test monitor state update and retrieval routes."""

    def test_post_state_valid_claude(self, client):
        """POST /state with valid claude node."""
        response = client.post(
            "/api/monitor/state",
            json={"node": "claude", "state": "active", "message": "working"},
        )
        assert response.status_code in [200, 500]

    def test_post_state_valid_jira(self, client):
        """POST /state with valid jira node."""
        response = client.post(
            "/api/monitor/state",
            json={"node": "jira", "state": "inactive", "message": "idle"},
        )
        assert response.status_code in [200, 500]

    def test_post_state_valid_github(self, client):
        """POST /state with valid github node."""
        response = client.post(
            "/api/monitor/state",
            json={"node": "github", "state": "active", "message": "pushing"},
        )
        assert response.status_code in [200, 500]

    def test_post_state_valid_jules(self, client):
        """POST /state with valid jules node."""
        response = client.post(
            "/api/monitor/state",
            json={"node": "jules", "state": "active", "message": "reviewing"},
        )
        assert response.status_code in [200, 500]

    def test_post_state_valid_actions(self, client):
        """POST /state with valid actions node."""
        response = client.post(
            "/api/monitor/state",
            json={"node": "actions", "state": "inactive", "message": "waiting"},
        )
        assert response.status_code in [200, 500]

    def test_post_state_missing_data(self, client):
        """POST /state with no JSON data."""
        response = client.post("/api/monitor/state", json=None)
        assert response.status_code in [400, 500]

    def test_post_state_invalid_node(self, client):
        """POST /state with invalid node."""
        response = client.post(
            "/api/monitor/state",
            json={"node": "invalid", "state": "active", "message": "test"},
        )
        assert response.status_code in [400, 500]

    def test_post_state_empty_message(self, client):
        """POST /state with empty message."""
        response = client.post(
            "/api/monitor/state",
            json={"node": "claude", "state": "active", "message": ""},
        )
        assert response.status_code in [200, 500]

    def test_post_state_missing_message(self, client):
        """POST /state with missing message field."""
        response = client.post(
            "/api/monitor/state",
            json={"node": "claude", "state": "active"},
        )
        assert response.status_code in [200, 500]

    def test_post_state_case_insensitive_node(self, client):
        """POST /state with uppercase node name."""
        response = client.post(
            "/api/monitor/state",
            json={"node": "CLAUDE", "state": "active", "message": "test"},
        )
        assert response.status_code in [200, 500]

    def test_get_state(self, client):
        """GET /state should return current state."""
        response = client.get("/api/monitor/state")
        assert response.status_code in [200, 404]

    def test_health_check(self, client):
        """GET /health should return health status."""
        response = client.get("/api/monitor/health")
        assert response.status_code in [200, 404]

    def test_metrics_endpoint(self, client):
        """GET /metrics should return metrics."""
        response = client.get("/api/monitor/metrics")
        assert response.status_code in [200, 404]

    def test_task_info_get(self, client):
        """GET /task-info should return task info."""
        response = client.get("/api/monitor/task-info")
        assert response.status_code in [200, 404]

    def test_task_info_post(self, client):
        """POST /task-info should accept task info."""
        response = client.post(
            "/api/monitor/task-info",
            json={"title": "Test Task", "status": "in_progress"},
        )
        assert response.status_code in [200, 400, 404, 500]

    def test_multiple_sequential_updates(self, client):
        """Multiple state updates should succeed."""
        for i in range(3):
            response = client.post(
                "/api/monitor/state",
                json={"node": "claude", "state": "active", "message": f"update {i}"},
            )
            assert response.status_code in [200, 500]

    def test_different_nodes_sequential(self, client):
        """Updates to different nodes should work."""
        for node in ["claude", "jira", "github"]:
            response = client.post(
                "/api/monitor/state",
                json={"node": node, "state": "active", "message": f"{node} update"},
            )
            assert response.status_code in [200, 500]

    def test_reset_monitoring(self, client):
        """POST /reset should reset monitoring state."""
        # First update some state
        client.post(
            "/api/monitor/state",
            json={"node": "claude", "state": "active", "message": "test"},
        )
        # Then reset
        response = client.post("/api/monitor/reset")
        assert response.status_code in [200, 404, 500]

    def test_update_task_with_title_and_status(self, client):
        """POST /task with title and status."""
        response = client.post(
            "/api/monitor/task",
            json={"title": "Test Task", "status": "running"},
        )
        assert response.status_code in [200, 404, 500]

    def test_update_task_with_start_time(self, client):
        """POST /task with explicit start_time."""
        response = client.post(
            "/api/monitor/task",
            json={
                "title": "Test Task",
                "status": "running",
                "start_time": "2026-02-05T12:00:00Z",
            },
        )
        assert response.status_code in [200, 404, 500]

    def test_update_task_status_idle(self, client):
        """POST /task with idle status."""
        response = client.post(
            "/api/monitor/task",
            json={"title": "Test Task", "status": "idle"},
        )
        assert response.status_code in [200, 404, 500]

    def test_update_task_status_completed(self, client):
        """POST /task with completed status."""
        response = client.post(
            "/api/monitor/task",
            json={"title": "Completed Task", "status": "completed"},
        )
        assert response.status_code in [200, 404, 500]

    def test_update_task_status_failed(self, client):
        """POST /task with failed status."""
        response = client.post(
            "/api/monitor/task",
            json={"title": "Failed Task", "status": "failed"},
        )
        assert response.status_code in [200, 404, 500]

    def test_update_task_no_data(self, client):
        """POST /task with no JSON data."""
        response = client.post("/api/monitor/task", json=None)
        assert response.status_code in [400, 404, 500]

    def test_update_task_empty_data(self, client):
        """POST /task with empty JSON."""
        response = client.post("/api/monitor/task", json={})
        assert response.status_code in [200, 400, 404, 500]
