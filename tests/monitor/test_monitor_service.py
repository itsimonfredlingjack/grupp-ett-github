"""Tests for MonitorService."""

import pytest

from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    """Tests for MonitorService class."""

    @pytest.fixture
    def service(self):
        """Fixture for MonitorService."""
        return MonitorService()

    def test_initial_state(self, service):
        """Test initial state of service."""
        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert "jira" in state["nodes"]
        assert state["task_info"]["status"] == "idle"

    def test_update_node_valid(self, service):
        """Test updating a valid node."""
        result = service.update_node("jira", "active", "Fetching ticket")
        assert result is True

        state = service.get_state()
        assert state["current_node"] == "jira"
        assert state["nodes"]["jira"]["active"] is True
        assert state["nodes"]["jira"]["message"] == "Fetching ticket"
        assert len(state["event_log"]) == 1
        assert state["event_log"][0]["node"] == "jira"

    def test_update_node_invalid(self, service):
        """Test updating an invalid node."""
        result = service.update_node("invalid_node", "active")
        assert result is False
        assert service.get_state()["current_node"] is None

    def test_node_transition(self, service):
        """Test transition between nodes."""
        service.update_node("jira", "active")
        service.update_node("claude", "active")

        state = service.get_state()
        assert state["current_node"] == "claude"
        assert state["nodes"]["jira"]["active"] is False
        assert state["nodes"]["claude"]["active"] is True

    def test_reset(self, service):
        """Test resetting state."""
        service.update_node("jira", "active")
        service.reset()

        state = service.get_state()
        assert state["current_node"] is None
        assert state["nodes"]["jira"]["active"] is False
        assert len(state["event_log"]) == 0

    def test_task_info(self, service):
        """Test updating task info."""
        service.set_task_info(title="Test Task", status="running")

        info = service.get_task_info()
        assert info["title"] == "Test Task"
        assert info["status"] == "running"
