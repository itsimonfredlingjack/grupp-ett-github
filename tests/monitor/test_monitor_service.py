"""Tests for MonitorService."""

import pytest
from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    @pytest.fixture
    def service(self):
        return MonitorService(max_events=10)

    def test_initialization(self, service):
        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["nodes"]) == 5  # jira, claude, github, jules, actions
        assert state["event_log"] == []
        assert state["task_info"]["status"] == "idle"

    def test_update_node_valid(self, service):
        success = service.update_node("claude", "active", "Coding now")
        assert success is True
        state = service.get_state()
        assert state["current_node"] == "claude"
        assert state["nodes"]["claude"]["active"] is True
        assert state["nodes"]["claude"]["message"] == "Coding now"
        assert len(state["event_log"]) == 1
        assert state["event_log"][0]["node"] == "claude"

    def test_update_node_invalid(self, service):
        success = service.update_node("invalid_node", "active", "msg")
        assert success is False
        assert len(service.event_log) == 0

    def test_node_deactivation_on_switch(self, service):
        service.update_node("jira", "active", "Reading ticket")
        service.update_node("claude", "active", "Writing code")

        state = service.get_state()
        assert state["nodes"]["jira"]["active"] is False
        assert state["nodes"]["claude"]["active"] is True
        assert state["current_node"] == "claude"

    def test_reset(self, service):
        service.update_node("claude", "active", "Working")
        service.set_task_info("Task 1", "running")

        service.reset()

        state = service.get_state()
        assert state["current_node"] is None
        assert state["nodes"]["claude"]["active"] is False
        assert state["event_log"] == []
        assert state["task_info"]["status"] == "idle"

    def test_event_log_limit(self, service):
        # Service initialized with max_events=10
        for i in range(15):
            service.update_node("claude", "active", f"Message {i}")

        assert len(service.event_log) == 10
        assert service.event_log[-1]["message"] == "Message 14"
        assert service.event_log[0]["message"] == "Message 5"

    def test_task_info(self, service):
        service.set_task_info("New Task", "running", "2023-01-01T00:00:00Z")
        info = service.get_task_info()

        assert info["title"] == "New Task"
        assert info["status"] == "running"
        assert info["start_time"] == "2023-01-01T00:00:00Z"

    def test_task_info_partial_update(self, service):
        service.set_task_info("Original Task", "running")
        service.set_task_info(status="completed")

        info = service.get_task_info()
        assert info["title"] == "Original Task"
        assert info["status"] == "completed"
