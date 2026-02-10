"""
Unit tests for MonitorService.
"""


import pytest

from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    @pytest.fixture
    def service(self):
        return MonitorService(max_events=10)

    def test_initialization(self, service):
        assert service.current_node is None
        assert len(service.nodes) == 5  # jira, claude, github, jules, actions
        assert len(service.event_log) == 0
        assert service.task_info["status"] == "idle"

    def test_update_node_valid(self, service):
        success = service.update_node("claude", "active", "Thinking...")
        assert success is True
        assert service.current_node == "claude"
        assert service.nodes["claude"].active is True
        assert service.nodes["claude"].message == "Thinking..."
        assert len(service.event_log) == 1

    def test_update_node_invalid(self, service):
        success = service.update_node("invalid_node", "active")
        assert success is False
        assert len(service.event_log) == 0

    def test_node_transition(self, service):
        # Activate Claude
        service.update_node("claude", "active")
        assert service.nodes["claude"].active is True

        # Switch to Jira
        service.update_node("jira", "active")
        assert service.nodes["claude"].active is False
        assert service.nodes["jira"].active is True
        assert service.current_node == "jira"

    def test_max_events_limit(self, service):
        for i in range(15):
            service.update_node("claude", "active", f"Message {i}")

        assert len(service.event_log) == 10
        assert service.event_log[-1]["message"] == "Message 14"

    def test_reset(self, service):
        service.update_node("claude", "active")
        service.set_task_info("Task 1", "running")

        service.reset()

        assert service.current_node is None
        assert len(service.event_log) == 0
        assert service.task_info["status"] == "idle"
        assert service.nodes["claude"].active is False

    def test_task_info(self, service):
        service.set_task_info("New Task", "running", "2023-01-01T00:00:00Z")
        info = service.get_task_info()

        assert info["title"] == "New Task"
        assert info["status"] == "running"
        assert info["start_time"] == "2023-01-01T00:00:00Z"

    def test_get_state(self, service):
        service.update_node("github", "active")
        state = service.get_state()

        assert state["current_node"] == "github"
        assert "nodes" in state
        assert "event_log" in state
        assert "task_info" in state
