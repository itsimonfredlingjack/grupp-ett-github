"""Tests for MonitorService."""

from datetime import datetime
from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    """Test suite for MonitorService."""

    def test_init(self):
        """Test initialization."""
        service = MonitorService()
        assert service.current_node is None
        assert len(service.nodes) == 5
        assert len(service.event_log) == 0
        assert service.task_info["status"] == "idle"

    def test_update_node_valid(self):
        """Test updating a valid node."""
        service = MonitorService()
        success = service.update_node("claude", "active", "Coding...")
        assert success
        assert service.nodes["claude"].active
        assert service.nodes["claude"].message == "Coding..."
        assert service.current_node == "claude"
        assert len(service.event_log) == 1

    def test_update_node_invalid(self):
        """Test updating an invalid node."""
        service = MonitorService()
        success = service.update_node("invalid_node", "active")
        assert not success

    def test_update_node_inactive(self):
        """Test deactivating a node."""
        service = MonitorService()
        service.update_node("claude", "active", "Start")
        service.update_node("claude", "inactive", "Stop")
        assert not service.nodes["claude"].active

    def test_node_switch(self):
        """Test switching active nodes."""
        service = MonitorService()
        service.update_node("claude", "active")
        service.update_node("github", "active")
        assert not service.nodes["claude"].active
        assert service.nodes["github"].active
        assert service.current_node == "github"

    def test_reset(self):
        """Test resetting the service."""
        service = MonitorService()
        service.update_node("claude", "active")
        service.set_task_info("Test Task", "running")
        service.reset()
        assert service.current_node is None
        assert not service.nodes["claude"].active
        assert len(service.event_log) == 0
        assert service.task_info["status"] == "idle"

    def test_set_task_info(self):
        """Test updating task info."""
        service = MonitorService()
        service.set_task_info("New Task", "running", "2023-01-01T00:00:00Z")
        assert service.task_info["title"] == "New Task"
        assert service.task_info["status"] == "running"
        assert service.task_info["start_time"] == "2023-01-01T00:00:00Z"

    def test_get_state(self):
        """Test getting full state."""
        service = MonitorService()
        service.update_node("claude", "active")
        state = service.get_state()
        assert state["current_node"] == "claude"
        assert "nodes" in state
        assert "event_log" in state
        assert "task_info" in state

    def test_event_log_limit(self):
        """Test event log max size."""
        service = MonitorService(max_events=2)
        service.add_event("jira", "1")
        service.add_event("claude", "2")
        service.add_event("github", "3")
        assert len(service.event_log) == 2
        assert service.event_log[0]["message"] == "2"
        assert service.event_log[1]["message"] == "3"
