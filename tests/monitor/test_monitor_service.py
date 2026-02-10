"""Tests for MonitorService."""

import pytest
from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    """Tests for MonitorService class."""

    @pytest.fixture
    def service(self):
        """Fixture for MonitorService."""
        return MonitorService(max_events=10)

    def test_initialization(self, service):
        """Test initial state."""
        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"
        assert len(state["nodes"]) == 5  # jira, claude, github, jules, actions

    def test_update_node_valid(self, service):
        """Test updating a valid node."""
        success = service.update_node("jira", "active", "Fetching ticket")
        assert success is True

        state = service.get_state()
        assert state["current_node"] == "jira"
        assert state["nodes"]["jira"]["active"] is True
        assert state["nodes"]["jira"]["message"] == "Fetching ticket"
        assert len(state["event_log"]) == 1
        assert state["event_log"][0]["node"] == "jira"

    def test_update_node_invalid(self, service):
        """Test updating an invalid node."""
        success = service.update_node("invalid_node", "active")
        assert success is False

        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0

    def test_node_transition(self, service):
        """Test transitioning between nodes."""
        service.update_node("jira", "active", "Start")
        service.update_node("claude", "active", "Thinking")

        state = service.get_state()
        assert state["current_node"] == "claude"
        assert state["nodes"]["claude"]["active"] is True
        assert state["nodes"]["jira"]["active"] is False  # Previous node deactivated
        assert len(state["event_log"]) == 2

    def test_message_truncation(self, service):
        """Test that long messages are truncated."""
        long_message = "a" * 300
        service.update_node("jira", "active", long_message)

        state = service.get_state()
        assert len(state["nodes"]["jira"]["message"]) == 200
        assert len(state["event_log"][0]["message"]) == 200

    def test_event_log_rotation(self, service):
        """Test that event log rotates after max_events."""
        for i in range(15):
            service.update_node("jira", "active", f"Message {i}")

        state = service.get_state()
        assert len(state["event_log"]) == 10  # Max events is 10
        assert state["event_log"][-1]["message"] == "Message 14"

    def test_reset(self, service):
        """Test resetting the service."""
        service.update_node("jira", "active", "Start")
        service.set_task_info("Task 1", "running")

        service.reset()

        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"
        assert state["nodes"]["jira"]["active"] is False

    def test_task_info(self, service):
        """Test setting and getting task info."""
        service.set_task_info("Fix bug", "running", "2023-01-01T12:00:00Z")

        info = service.get_task_info()
        assert info["title"] == "Fix bug"
        assert info["status"] == "running"
        assert info["start_time"] == "2023-01-01T12:00:00Z"

    def test_task_info_partial_update(self, service):
        """Test partially updating task info."""
        service.set_task_info("Initial Task", "running")
        service.set_task_info(status="completed")

        info = service.get_task_info()
        assert info["title"] == "Initial Task"
        assert info["status"] == "completed"
