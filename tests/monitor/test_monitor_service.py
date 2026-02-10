"""Tests for MonitorService."""

from datetime import datetime

import pytest

from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    @pytest.fixture
    def service(self):
        return MonitorService(max_events=10)

    def test_initial_state(self, service):
        """Test initial state of the service."""
        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"
        assert len(state["nodes"]) == 5  # 5 valid nodes

    def test_update_node_valid(self, service):
        """Test updating a valid node."""
        success = service.update_node("claude", "active", "Processing")
        assert success is True
        state = service.get_state()
        assert state["current_node"] == "claude"
        assert state["nodes"]["claude"]["active"] is True
        assert state["nodes"]["claude"]["message"] == "Processing"
        assert len(state["event_log"]) == 1

    def test_update_node_invalid(self, service):
        """Test updating an invalid node."""
        success = service.update_node("invalid_node", "active", "Processing")
        assert success is False
        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0

    def test_update_node_transition(self, service):
        """Test transitioning between nodes."""
        service.update_node("claude", "active", "Step 1")
        service.update_node("jules", "active", "Step 2")

        state = service.get_state()
        assert state["current_node"] == "jules"
        assert state["nodes"]["claude"]["active"] is False  # Previous node deactivated
        assert state["nodes"]["jules"]["active"] is True
        assert len(state["event_log"]) == 2

    def test_event_log_limit(self, service):
        """Test that event log respects max_events."""
        for i in range(15):
            service.add_event("claude", f"Message {i}")

        state = service.get_state()
        assert len(state["event_log"]) == 10
        assert state["event_log"][-1]["message"] == "Message 14"

    def test_reset(self, service):
        """Test resetting the service."""
        service.update_node("claude", "active", "Processing")
        service.set_task_info("Task 1", "running")

        service.reset()

        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"
        assert state["nodes"]["claude"]["active"] is False

    def test_task_info(self, service):
        """Test setting and getting task info."""
        now = datetime.utcnow().isoformat() + "Z"
        service.set_task_info("New Task", "running", now)

        info = service.get_task_info()
        assert info["title"] == "New Task"
        assert info["status"] == "running"
        assert info["start_time"] == now

    def test_task_info_partial_update(self, service):
        """Test updating only some fields of task info."""
        service.set_task_info("Task 1", "running")
        service.set_task_info(status="completed")

        info = service.get_task_info()
        assert info["title"] == "Task 1"
        assert info["status"] == "completed"

    def test_message_truncation(self, service):
        """Test that long messages are truncated."""
        long_message = "a" * 300
        service.update_node("claude", "active", long_message)

        state = service.get_state()
        assert len(state["nodes"]["claude"]["message"]) == 200
        assert len(state["event_log"][0]["message"]) == 200

    def test_task_title_truncation(self, service):
        """Test that long task titles are truncated."""
        long_title = "t" * 150
        service.set_task_info(title=long_title)

        info = service.get_task_info()
        assert len(info["title"]) == 100
