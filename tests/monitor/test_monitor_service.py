"""Tests for MonitorService."""

import pytest
from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    """Tests for MonitorService business logic."""

    @pytest.fixture
    def service(self):
        """Create a fresh service instance."""
        return MonitorService()

    def test_initial_state(self, service):
        """Test initial state of the service."""
        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"
        assert "jira" in state["nodes"]

    def test_update_node_valid(self, service):
        """Test updating a valid node."""
        success = service.update_node("jira", "active", "Fetching issues")
        assert success is True

        state = service.get_state()
        assert state["current_node"] == "jira"
        assert state["nodes"]["jira"]["active"] is True
        assert state["nodes"]["jira"]["message"] == "Fetching issues"
        assert len(state["event_log"]) == 1

    def test_update_node_invalid(self, service):
        """Test updating an invalid node."""
        success = service.update_node("invalid_node", "active")
        assert success is False

        state = service.get_state()
        assert state["current_node"] is None

    def test_node_transition(self, service):
        """Test transitioning between nodes."""
        service.update_node("jira", "active", "Step 1")
        service.update_node("claude", "active", "Step 2")

        state = service.get_state()
        assert state["current_node"] == "claude"
        assert state["nodes"]["jira"]["active"] is False
        assert state["nodes"]["claude"]["active"] is True
        assert len(state["event_log"]) == 2

    def test_reset(self, service):
        """Test resetting the service."""
        service.update_node("jira", "active", "Working")
        service.set_task_info("Task 1", "running")

        service.reset()

        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"

    def test_event_log_limit(self, service):
        """Test event log size limit."""
        service = MonitorService(max_events=5)
        for i in range(10):
            service.add_event("jira", f"Message {i}")

        assert len(service.event_log) == 5
        assert service.event_log[-1]["message"] == "Message 9"

    def test_task_info_update(self, service):
        """Test updating task info."""
        service.set_task_info("New Task", "running", "2026-01-01T12:00:00Z")

        info = service.get_task_info()
        assert info["title"] == "New Task"
        assert info["status"] == "running"
        assert info["start_time"] == "2026-01-01T12:00:00Z"

    def test_task_info_partial_update(self, service):
        """Test partial update of task info."""
        service.set_task_info("Original Task", "running")
        service.set_task_info(status="completed")

        info = service.get_task_info()
        assert info["title"] == "Original Task"
        assert info["status"] == "completed"
