"""Unit tests for MonitorService."""

import pytest
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def service():
    """Fixture for MonitorService."""
    return MonitorService()


class TestMonitorService:
    """Test suite for MonitorService."""

    def test_initial_state(self, service):
        """Test initial state of the service."""
        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"
        assert all(not node["active"] for node in state["nodes"].values())

    def test_update_node_valid(self, service):
        """Test updating a valid node."""
        success = service.update_node("claude", "active", "Thinking...")
        assert success

        state = service.get_state()
        assert state["current_node"] == "claude"
        assert state["nodes"]["claude"]["active"] is True
        assert state["nodes"]["claude"]["message"] == "Thinking..."
        assert len(state["event_log"]) == 1
        assert state["event_log"][0]["node"] == "claude"
        assert state["event_log"][0]["message"] == "Thinking..."

    def test_update_node_invalid(self, service):
        """Test updating an invalid node."""
        success = service.update_node("invalid_node", "active")
        assert not success

        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0

    def test_update_node_transitions(self, service):
        """Test transitioning between nodes."""
        service.update_node("claude", "active")
        service.update_node("github", "active")

        state = service.get_state()
        assert state["current_node"] == "github"
        assert state["nodes"]["github"]["active"] is True
        assert state["nodes"]["claude"]["active"] is False  # Should be deactivated

    def test_reset(self, service):
        """Test resetting the service."""
        service.update_node("claude", "active")
        service.set_task_info("Task 1", "running")

        service.reset()

        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"

    def test_set_task_info(self, service):
        """Test updating task info."""
        service.set_task_info("Fix Bug", "running", "2023-01-01T12:00:00Z")

        task_info = service.get_task_info()
        assert task_info["title"] == "Fix Bug"
        assert task_info["status"] == "running"
        assert task_info["start_time"] == "2023-01-01T12:00:00Z"

    def test_event_log_limit(self, service):
        """Test event log size limit."""
        service.max_events = 5
        for i in range(10):
            service.add_event("claude", f"Message {i}")

        assert len(service.event_log) == 5
        assert service.event_log[-1]["message"] == "Message 9"
