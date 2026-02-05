"""Tests for MonitorService."""

import pytest

from src.sejfa.monitor.monitor_service import MonitorService, WorkflowNode


class TestMonitorService:
    """Tests for MonitorService class."""

    @pytest.fixture
    def service(self) -> MonitorService:
        """Create a fresh MonitorService instance."""
        return MonitorService()

    def test_initialization(self, service: MonitorService) -> None:
        """Test initial state."""
        assert service.current_node is None
        assert len(service.nodes) == 5  # jira, claude, github, jules, actions
        assert isinstance(service.nodes["jira"], WorkflowNode)
        assert not service.nodes["jira"].active
        assert service.event_log == []
        assert service.task_info["status"] == "idle"

    def test_update_node_valid(self, service: MonitorService) -> None:
        """Test updating a valid node."""
        success = service.update_node("jira", "active", "Fetching ticket")
        assert success
        assert service.current_node == "jira"
        assert service.nodes["jira"].active
        assert service.nodes["jira"].message == "Fetching ticket"
        assert len(service.event_log) == 1
        assert service.event_log[0]["node"] == "jira"
        assert service.event_log[0]["message"] == "Fetching ticket"

    def test_update_node_invalid(self, service: MonitorService) -> None:
        """Test updating an invalid node."""
        success = service.update_node("invalid_node", "active")
        assert not success
        assert service.current_node is None
        assert len(service.event_log) == 0

    def test_update_node_deactivates_previous(self, service: MonitorService) -> None:
        """Test that activating a new node deactivates the previous one."""
        service.update_node("jira", "active")
        assert service.nodes["jira"].active

        service.update_node("claude", "active")
        assert not service.nodes["jira"].active
        assert service.nodes["claude"].active
        assert service.current_node == "claude"

    def test_update_node_inactive(self, service: MonitorService) -> None:
        """Test setting a node to inactive."""
        service.update_node("jira", "active")
        assert service.nodes["jira"].active

        service.update_node("jira", "inactive")
        assert not service.nodes["jira"].active
        # Current node pointer remains until another activates (or reset)
        assert service.current_node == "jira"

    def test_event_log_limit(self, service: MonitorService) -> None:
        """Test that event log size is limited."""
        service.max_events = 3
        for i in range(5):
            service.add_event("jira", f"Message {i}")

        assert len(service.event_log) == 3
        assert service.event_log[0]["message"] == "Message 2"
        assert service.event_log[2]["message"] == "Message 4"

    def test_reset(self, service: MonitorService) -> None:
        """Test resetting state."""
        service.update_node("jira", "active")
        service.set_task_info("Task 1", "running")

        service.reset()

        assert service.current_node is None
        assert not service.nodes["jira"].active
        assert service.event_log == []
        assert service.task_info["status"] == "idle"

    def test_task_info(self, service: MonitorService) -> None:
        """Test task info management."""
        service.set_task_info("My Task", "running", "2023-01-01T12:00:00Z")
        info = service.get_task_info()

        assert info["title"] == "My Task"
        assert info["status"] == "running"
        assert info["start_time"] == "2023-01-01T12:00:00Z"

    def test_get_state(self, service: MonitorService) -> None:
        """Test getting full state snapshot."""
        service.update_node("jira", "active", "Working")
        state = service.get_state()

        assert state["current_node"] == "jira"
        assert "nodes" in state
        assert "event_log" in state
        assert "task_info" in state
        assert state["nodes"]["jira"]["active"] is True
