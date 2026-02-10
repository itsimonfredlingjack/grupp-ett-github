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
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"
        assert len(state["nodes"]) == 5  # 5 valid nodes

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
        assert state["event_log"][0]["message"] == "Thinking..."

    def test_update_node_invalid(self, service):
        """Test updating an invalid node."""
        success = service.update_node("invalid_node", "active", "msg")
        assert success is False
        assert service.current_node is None

    def test_node_transition(self, service):
        """Test transition from one node to another."""
        service.update_node("claude", "active", "Step 1")
        service.update_node("github", "active", "Step 2")

        state = service.get_state()
        assert state["current_node"] == "github"
        assert state["nodes"]["github"]["active"] is True
        assert state["nodes"]["claude"]["active"] is False  # Previous node deactivated
        assert len(state["event_log"]) == 2

    def test_reset(self, service):
        """Test resetting the service."""
        service.update_node("claude", "active", "msg")
        service.set_task_info("Task 1", "running")

        service.reset()

        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"
        assert all(not node["active"] for node in state["nodes"].values())

    def test_set_task_info(self, service):
        """Test updating task info."""
        service.set_task_info("New Task", "running", "2023-01-01T00:00:00Z")

        info = service.get_task_info()
        assert info["title"] == "New Task"
        assert info["status"] == "running"
        assert info["start_time"] == "2023-01-01T00:00:00Z"

    def test_set_task_info_partial_update(self, service):
        """Test partial update of task info."""
        service.set_task_info(title="Task 1")
        service.set_task_info(status="completed")

        info = service.get_task_info()
        assert info["title"] == "Task 1"
        assert info["status"] == "completed"

    def test_event_log_limit(self, service):
        """Test event log size limit."""
        service.max_events = 5
        for i in range(10):
            service.add_event("claude", f"msg {i}")

        assert len(service.event_log) == 5
        assert service.event_log[-1]["message"] == "msg 9"
