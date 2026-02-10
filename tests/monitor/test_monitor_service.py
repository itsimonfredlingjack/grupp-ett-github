"""Unit tests for MonitorService."""

import pytest
from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    """Test suite for MonitorService."""

    @pytest.fixture
    def service(self) -> MonitorService:
        """Create a fresh MonitorService instance."""
        return MonitorService()

    def test_initial_state(self, service: MonitorService) -> None:
        """Test initial state of the service."""
        state = service.get_state()
        assert state["current_node"] is None
        assert "claude" in state["nodes"]
        assert state["nodes"]["claude"]["active"] is False
        assert state["task_info"] == {
            "title": "Waiting for task...",
            "status": "idle",
            "start_time": None,
        }
        assert state["event_log"] == []

    def test_update_node(self, service: MonitorService) -> None:
        """Test updating a node state."""
        service.update_node("claude", "active", "Thinking...")
        state = service.get_state()
        assert state["nodes"]["claude"]["active"] is True
        assert state["current_node"] == "claude"
        assert len(state["event_log"]) == 1
        assert state["event_log"][0]["message"] == "Thinking..."
        assert state["event_log"][0]["node"] == "claude"

    def test_update_node_invalid_node(self, service: MonitorService) -> None:
        """Test updating an invalid node returns False."""
        result = service.update_node("invalid", "active", "msg")
        assert result is False
        state = service.get_state()
        assert "invalid" not in state["nodes"]

    def test_set_task_info(self, service: MonitorService) -> None:
        """Test updating task info."""
        service.set_task_info("Fix bug", "running", "2023-01-01T00:00:00Z")
        state = service.get_state()
        assert state["task_info"]["title"] == "Fix bug"
        assert state["task_info"]["status"] == "running"
        assert state["task_info"]["start_time"] == "2023-01-01T00:00:00Z"

    def test_reset(self, service: MonitorService) -> None:
        """Test resetting the service."""
        service.update_node("claude", "active", "msg")
        service.set_task_info("Task", "running", "time")
        service.reset()
        state = service.get_state()
        assert state["nodes"]["claude"]["active"] is False
        assert state["current_node"] is None
        assert state["task_info"]["status"] == "idle"
        assert state["event_log"] == []
