"""Tests for MonitorService."""

import pytest

from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    """Tests for the MonitorService class."""

    @pytest.fixture
    def service(self) -> MonitorService:
        """Create a MonitorService instance."""
        return MonitorService()

    def test_initialization(self, service: MonitorService) -> None:
        """Test initial state."""
        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert len(state["nodes"]) == 5  # 5 valid nodes
        assert state["task_info"]["status"] == "idle"

    def test_update_node_valid(self, service: MonitorService) -> None:
        """Test updating a valid node."""
        success = service.update_node("claude", "active", "Thinking")
        assert success is True

        state = service.get_state()
        assert state["current_node"] == "claude"
        assert state["nodes"]["claude"]["active"] is True
        assert state["nodes"]["claude"]["message"] == "Thinking"
        assert len(state["event_log"]) == 1
        assert state["event_log"][0]["node"] == "claude"
        assert state["event_log"][0]["message"] == "Thinking"

    def test_update_node_invalid(self, service: MonitorService) -> None:
        """Test updating an invalid node."""
        success = service.update_node("invalid_node", "active")
        assert success is False

        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0

    def test_node_transition(self, service: MonitorService) -> None:
        """Test transitioning between nodes."""
        service.update_node("claude", "active")
        service.update_node("github", "active")

        state = service.get_state()
        assert state["current_node"] == "github"
        assert state["nodes"]["github"]["active"] is True
        assert (
            state["nodes"]["claude"]["active"] is False
        )  # Previous node should deactivate

    def test_reset(self, service: MonitorService) -> None:
        """Test resetting the service."""
        service.update_node("claude", "active")
        service.reset()

        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["nodes"]["claude"]["active"] is False

    def test_set_task_info(self, service: MonitorService) -> None:
        """Test updating task info."""
        service.set_task_info("Fix bug", "running", "2023-01-01T00:00:00Z")

        info = service.get_task_info()
        assert info["title"] == "Fix bug"
        assert info["status"] == "running"
        assert info["start_time"] == "2023-01-01T00:00:00Z"

    def test_event_log_limit(self) -> None:
        """Test that event log respects max_events."""
        service = MonitorService(max_events=2)
        service.add_event("n1", "m1")
        service.add_event("n2", "m2")
        service.add_event("n3", "m3")

        state = service.get_state()
        assert len(state["event_log"]) == 2
        assert state["event_log"][0]["node"] == "n2"
        assert state["event_log"][1]["node"] == "n3"
