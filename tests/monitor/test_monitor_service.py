"""Tests for MonitorService."""

import pytest
from src.sejfa.monitor.monitor_service import MonitorService, WorkflowNode


class TestMonitorService:
    """Tests for MonitorService class."""

    @pytest.fixture
    def service(self):
        """Create a MonitorService instance."""
        return MonitorService(max_events=10)

    def test_initialization(self, service):
        """Test initial state."""
        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert len(state["nodes"]) == 5  # 5 valid nodes
        assert state["task_info"]["status"] == "idle"

    def test_update_node_valid(self, service):
        """Test updating a valid node."""
        result = service.update_node("claude", "active", "Thinking...")
        assert result is True

        state = service.get_state()
        assert state["current_node"] == "claude"
        assert state["nodes"]["claude"]["active"] is True
        assert state["nodes"]["claude"]["message"] == "Thinking..."
        assert len(state["event_log"]) == 1

    def test_update_node_invalid(self, service):
        """Test updating an invalid node."""
        result = service.update_node("invalid_node", "active")
        assert result is False
        assert len(service.event_log) == 0

    def test_update_node_inactive(self, service):
        """Test deactivating a node."""
        service.update_node("claude", "active")
        service.update_node("claude", "inactive")

        state = service.get_state()
        assert state["nodes"]["claude"]["active"] is False

    def test_node_transition(self, service):
        """Test transitioning from one node to another."""
        service.update_node("claude", "active")
        service.update_node("github", "active")

        state = service.get_state()
        assert state["current_node"] == "github"
        assert state["nodes"]["github"]["active"] is True
        assert state["nodes"]["claude"]["active"] is False  # Should deactivate previous

    def test_event_log_truncation(self, service):
        """Test that event log respects max_events."""
        for i in range(15):
            service.update_node("claude", "active", f"Message {i}")

        assert len(service.event_log) == 10
        assert service.event_log[-1]["message"] == "Message 14"

    def test_task_info(self, service):
        """Test setting task info."""
        service.set_task_info(title="Fix bugs", status="running", start_time="2023-01-01")

        info = service.get_task_info()
        assert info["title"] == "Fix bugs"
        assert info["status"] == "running"
        assert info["start_time"] == "2023-01-01"

    def test_reset(self, service):
        """Test resetting the service."""
        service.update_node("claude", "active")
        service.set_task_info(title="Test")

        service.reset()

        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["title"] == "Waiting for task..."
