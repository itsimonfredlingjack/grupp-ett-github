"""Tests for MonitorService."""

import pytest

from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    @pytest.fixture
    def service(self):
        return MonitorService(max_events=10)

    def test_initial_state(self, service):
        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert "jira" in state["nodes"]
        assert state["nodes"]["jira"]["active"] is False

    def test_update_node_activates_node(self, service):
        service.update_node("jira", "active", "Fetching ticket")
        state = service.get_state()
        assert state["current_node"] == "jira"
        assert state["nodes"]["jira"]["active"] is True
        assert state["nodes"]["jira"]["message"] == "Fetching ticket"
        assert len(state["event_log"]) == 1
        assert state["event_log"][0]["node"] == "jira"

    def test_update_node_deactivates_previous(self, service):
        service.update_node("jira", "active", "Start")
        service.update_node("claude", "active", "Coding")

        state = service.get_state()
        assert state["current_node"] == "claude"
        assert state["nodes"]["claude"]["active"] is True
        assert state["nodes"]["jira"]["active"] is False

    def test_invalid_node_ignored(self, service):
        result = service.update_node("invalid_node", "active", "msg")
        assert result is False
        assert service.current_node is None

    def test_event_log_limit(self, service):
        for i in range(15):
            service.update_node("jira", "active", f"msg {i}")

        state = service.get_state()
        assert len(state["event_log"]) == 10
        assert state["event_log"][-1]["message"] == "msg 14"

    def test_reset(self, service):
        service.update_node("jira", "active", "msg")
        service.reset()

        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"

    def test_task_info(self, service):
        service.set_task_info("Test Task", "running", "2024-01-01T00:00:00Z")
        info = service.get_task_info()

        assert info["title"] == "Test Task"
        assert info["status"] == "running"
        assert info["start_time"] == "2024-01-01T00:00:00Z"
