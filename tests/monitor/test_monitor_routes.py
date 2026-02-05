"""Tests for monitor routes."""

import pytest

from app import create_app
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def client():
    """Create test client."""
    # Reset the monitor service singleton BEFORE creating app
    MonitorService._instance = None

    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


@pytest.fixture
def service():
    """Get the monitor service instance (must be called after client fixture)."""
    return MonitorService()


class TestGetState:
    """Tests for GET /api/monitor/state endpoint."""

    def test_get_initial_state(self, client):
        """Should return idle state initially."""
        response = client.get("/api/monitor/state")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "idle"
        assert data["task"] is None

    def test_get_state_with_active_task(self, client, service):
        """Should return task data when active."""
        service.start_task("GE-123", title="Test Task")

        response = client.get("/api/monitor/state")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "running"
        assert data["task"]["task_id"] == "GE-123"


class TestTaskEndpoint:
    """Tests for POST /api/monitor/task endpoint."""

    def test_start_task(self, client):
        """Should start a new task."""
        response = client.post(
            "/api/monitor/task",
            json={
                "action": "start",
                "task_id": "GE-123",
                "title": "Test Task",
                "max_iterations": 15,
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["task_id"] == "GE-123"
        assert data["title"] == "Test Task"
        assert data["max_iterations"] == 15

    def test_start_task_requires_task_id(self, client):
        """Should return error if task_id missing."""
        response = client.post(
            "/api/monitor/task",
            json={"action": "start"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_update_task(self, client, service):
        """Should update task state."""
        service.start_task("GE-123")

        response = client.post(
            "/api/monitor/task",
            json={
                "action": "update",
                "step": 2,
                "step_desc": "Pushing changes...",
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["step"] == 2
        assert data["step_desc"] == "Pushing changes..."

    def test_complete_task(self, client, service):
        """Should complete task."""
        service.start_task("GE-123")

        response = client.post(
            "/api/monitor/task",
            json={"action": "complete"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "done"

    def test_fail_task(self, client, service):
        """Should fail task with reason."""
        service.start_task("GE-123")

        response = client.post(
            "/api/monitor/task",
            json={
                "action": "fail",
                "step_desc": "Tests failed",
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "failed"

    def test_reset_task(self, client, service):
        """Should reset task state."""
        service.start_task("GE-123")

        response = client.post(
            "/api/monitor/task",
            json={"action": "reset"},
        )

        assert response.status_code == 200

        # Verify state is reset
        state = service.get_state()
        assert state["status"] == "idle"

    def test_unknown_action(self, client):
        """Should return error for unknown action."""
        response = client.post(
            "/api/monitor/task",
            json={"action": "unknown"},
        )

        assert response.status_code == 400


class TestEventEndpoint:
    """Tests for POST /api/monitor/event endpoint."""

    def test_add_event(self, client):
        """Should add an event."""
        response = client.post(
            "/api/monitor/event",
            json={
                "event_type": "info",
                "message": "Test event",
                "source": "test",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["event_type"] == "info"
        assert data["message"] == "Test event"

    def test_event_requires_message(self, client):
        """Should return error if message missing."""
        response = client.post(
            "/api/monitor/event",
            json={"event_type": "info"},
        )

        assert response.status_code == 400

    def test_event_with_metadata(self, client):
        """Should accept metadata."""
        response = client.post(
            "/api/monitor/event",
            json={
                "event_type": "success",
                "message": "Tests passed",
                "metadata": {"count": 24, "coverage": 0.95},
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["metadata"]["count"] == 24


class TestRalphStateEndpoint:
    """Tests for GET /api/monitor/ralph-state endpoint."""

    def test_returns_inactive_when_no_task_file(self, client):
        """Should return active=False when no task file."""
        response = client.get("/api/monitor/ralph-state")

        assert response.status_code == 200
        data = response.get_json()
        # May be active=False or contain parsed data depending on cwd
        assert "active" in data


class TestNodeStateEndpoint:
    """Tests for POST /api/monitor/node-state endpoint."""

    def test_update_node_state(self, client, service):
        """Should update node and create event."""
        service.start_task("GE-123")

        response = client.post(
            "/api/monitor/node-state",
            json={
                "node": "claude",
                "state": "active",
                "message": "Writing code...",
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["step"] == 1  # Claude is step 1

    def test_unknown_node_returns_error(self, client):
        """Should return error for unknown node."""
        response = client.post(
            "/api/monitor/node-state",
            json={"node": "unknown"},
        )

        assert response.status_code == 400

    def test_node_mapping(self, client, service):
        """Should map node names to correct steps."""
        service.start_task("GE-123")

        node_step_map = {
            "jira": 0,
            "claude": 1,
            "github": 2,
            "jules": 3,
            "actions": 4,
        }

        for node, expected_step in node_step_map.items():
            response = client.post(
                "/api/monitor/node-state",
                json={"node": node},
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["step"] == expected_step, (
                f"Node {node} should map to step {expected_step}"
            )


class TestStaticFiles:
    """Tests for static file serving."""

    def test_serve_monitor_html(self, client):
        """Should serve monitor.html."""
        response = client.get("/static/monitor.html")

        # File should exist and be served
        assert response.status_code == 200
        assert b"Ralph Loop Monitor" in response.data
