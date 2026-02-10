"""Tests for MonitorService."""

import pytest

from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def service():
    """Create a fresh MonitorService for each test."""
    return MonitorService()


class TestMonitorService:
    """Test cases for MonitorService."""

    def test_initial_state(self, service):
        """Test initial state of the service."""
        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"
        assert len(state["nodes"]) == 5  # jira, claude, github, jules, actions

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
        success = service.update_node("invalid_node", "active", "msg")
        assert success is False
        assert service.get_state()["current_node"] is None

    def test_update_node_deactivates_previous(self, service):
        """Test that activating a new node deactivates the previous one."""
        service.update_node("jira", "active", "Fetching")
        assert service.nodes["jira"].active is True

        service.update_node("claude", "active", "Thinking")
        assert service.nodes["jira"].active is False
        assert service.nodes["claude"].active is True
        assert service.current_node == "claude"

    def test_reset(self, service):
        """Test resetting the service."""
        service.update_node("jira", "active", "msg")
        service.set_task_info("Task 1", "running")

        service.reset()

        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"
        assert not state["nodes"]["jira"]["active"]

    def test_set_task_info(self, service):
        """Test updating task info."""
        service.set_task_info("New Task", "running", "2023-01-01T00:00:00Z")
        info = service.get_task_info()

        assert info["title"] == "New Task"
        assert info["status"] == "running"
        assert info["start_time"] == "2023-01-01T00:00:00Z"

    def test_event_log_limit(self, service):
        """Test that event log respects max_events."""
        service = MonitorService(max_events=5)
        for i in range(10):
            service.add_event("jira", f"msg {i}")

        assert len(service.event_log) == 5
        assert service.event_log[-1]["message"] == "msg 9"
