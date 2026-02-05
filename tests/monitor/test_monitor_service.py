"""Unit tests for MonitorService."""

import pytest
from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    """Tests for MonitorService."""

    @pytest.fixture
    def service(self):
        """Fixture providing a fresh MonitorService instance."""
        return MonitorService(max_events=10)

    def test_initialization(self, service):
        """Test initial state of the service."""
        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"
        assert all(not node["active"] for node in state["nodes"].values())

    def test_update_node_valid(self, service):
        """Test updating a valid node."""
        success = service.update_node("claude", "active", "Thinking...")
        assert success is True

        state = service.get_state()
        assert state["current_node"] == "claude"
        assert state["nodes"]["claude"]["active"] is True
        assert state["nodes"]["claude"]["message"] == "Thinking..."
        assert len(state["event_log"]) == 1
        assert state["event_log"][0]["node"] == "claude"

    def test_update_node_invalid(self, service):
        """Test updating an invalid node."""
        success = service.update_node("invalid_node", "active", "Test")
        assert success is False

        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0

    def test_node_transition(self, service):
        """Test transitioning between nodes."""
        service.update_node("jira", "active", "Reading ticket")
        service.update_node("claude", "active", "Processing")

        state = service.get_state()
        assert state["current_node"] == "claude"
        assert state["nodes"]["claude"]["active"] is True
        assert state["nodes"]["jira"]["active"] is False  # Should be deactivated
        assert len(state["event_log"]) == 2

    def test_update_node_inactive(self, service):
        """Test setting a node to inactive."""
        service.update_node("claude", "active", "Working")
        service.update_node("claude", "inactive", "Done")

        state = service.get_state()
        assert state["nodes"]["claude"]["active"] is False
        # Current node pointer remains until another becomes active
        assert state["current_node"] == "claude"

    def test_event_log_limit(self, service):
        """Test that event log respects max_events."""
        for i in range(15):
            service.add_event("system", f"Event {i}")

        state = service.get_state()
        assert len(state["event_log"]) == 10
        assert state["event_log"][-1]["message"] == "Event 14"
        assert state["event_log"][0]["message"] == "Event 5"

    def test_reset(self, service):
        """Test resetting the service."""
        service.update_node("claude", "active", "Test")
        service.set_task_info("Task 1", "running")

        service.reset()

        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["title"] == "Waiting for task..."
        assert state["task_info"]["status"] == "idle"

    def test_task_info(self, service):
        """Test updating task info."""
        service.set_task_info(title="Fix bug", status="running", start_time="2023-01-01T12:00:00Z")

        info = service.get_task_info()
        assert info["title"] == "Fix bug"
        assert info["status"] == "running"
        assert info["start_time"] == "2023-01-01T12:00:00Z"

    def test_task_info_partial_update(self, service):
        """Test partial update of task info."""
        service.set_task_info(title="Original", status="running")
        service.set_task_info(status="completed")

        info = service.get_task_info()
        assert info["title"] == "Original"
        assert info["status"] == "completed"
