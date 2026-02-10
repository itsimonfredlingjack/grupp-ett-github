"""Tests for MonitorService."""

import pytest
from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    @pytest.fixture
    def service(self):
        return MonitorService()

    def test_init(self, service):
        assert service.current_node is None
        assert "jira" in service.nodes
        assert len(service.event_log) == 0
        assert service.task_info["status"] == "idle"

    def test_update_node_valid(self, service):
        success = service.update_node("jira", "active", "Fetching ticket")
        assert success is True
        assert service.current_node == "jira"
        assert service.nodes["jira"].active is True
        assert service.nodes["jira"].message == "Fetching ticket"
        assert len(service.event_log) == 1

    def test_update_node_invalid(self, service):
        success = service.update_node("invalid_node", "active")
        assert success is False
        assert len(service.event_log) == 0

    def test_update_node_inactive(self, service):
        service.update_node("jira", "active")
        service.update_node("jira", "inactive")
        assert service.nodes["jira"].active is False

    def test_update_node_switch(self, service):
        service.update_node("jira", "active")
        service.update_node("claude", "active")
        assert service.nodes["jira"].active is False
        assert service.nodes["claude"].active is True
        assert service.current_node == "claude"

    def test_get_state(self, service):
        service.update_node("jira", "active")
        state = service.get_state()
        assert state["current_node"] == "jira"
        assert "nodes" in state
        assert "event_log" in state
        assert "task_info" in state

    def test_reset(self, service):
        service.update_node("jira", "active")
        service.set_task_info("Test Task", "running")
        service.reset()
        assert service.current_node is None
        assert service.nodes["jira"].active is False
        assert len(service.event_log) == 0
        assert service.task_info["status"] == "idle"

    def test_set_task_info(self, service):
        service.set_task_info("My Task", "running", "2023-01-01T00:00:00Z")
        info = service.get_task_info()
        assert info["title"] == "My Task"
        assert info["status"] == "running"
        assert info["start_time"] == "2023-01-01T00:00:00Z"

    def test_event_log_limit(self, service):
        service.max_events = 5
        for i in range(10):
            service.add_event("jira", f"Message {i}")
        assert len(service.event_log) == 5
        assert service.event_log[-1]["message"] == "Message 9"
