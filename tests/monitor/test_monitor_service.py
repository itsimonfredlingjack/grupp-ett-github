"""Tests for MonitorService."""

import pytest

from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    """Tests for MonitorService class."""

    @pytest.fixture
    def service(self):
        """Create a MonitorService instance."""
        return MonitorService()

    def test_initial_state(self, service):
        """Test initial state of the service."""
        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["nodes"]) == 5  # jira, claude, github, jules, actions
        assert state["nodes"]["jira"]["active"] is False
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"

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
        success = service.update_node("invalid_node", "active", "test")
        assert success is False
        state = service.get_state()
        assert state["current_node"] is None

    def test_node_transition(self, service):
        """Test transitioning between nodes."""
        service.update_node("jira", "active", "Step 1")
        service.update_node("claude", "active", "Step 2")

        state = service.get_state()
        assert state["current_node"] == "claude"
        assert state["nodes"]["claude"]["active"] is True
        assert state["nodes"]["jira"]["active"] is False  # Should be deactivated
        assert len(state["event_log"]) == 2

    def test_reset(self, service):
        """Test resetting the service."""
        service.update_node("jira", "active", "test")
        service.reset()

        state = service.get_state()
        assert state["current_node"] is None
        assert state["nodes"]["jira"]["active"] is False
        assert len(state["event_log"]) == 0

    def test_task_info(self, service):
        """Test updating task info."""
        service.set_task_info("New Task", "running", "2024-01-01T00:00:00Z")
        task = service.get_task_info()
        assert task["title"] == "New Task"
        assert task["status"] == "running"
        assert task["start_time"] == "2024-01-01T00:00:00Z"
