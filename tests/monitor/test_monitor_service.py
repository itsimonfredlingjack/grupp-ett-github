"""Tests for MonitorService."""

from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    def test_initialization(self):
        service = MonitorService(max_events=10)
        assert service.max_events == 10
        assert service.current_node is None
        assert len(service.nodes) == 5
        assert len(service.event_log) == 0

    def test_update_node_valid(self):
        service = MonitorService()
        success = service.update_node("jira", "active", "Fetching stuff")

        assert success is True
        assert service.current_node == "jira"
        assert service.nodes["jira"].active is True
        assert service.nodes["jira"].message == "Fetching stuff"
        assert len(service.event_log) == 1
        assert service.event_log[0]["node"] == "jira"

    def test_update_node_invalid(self):
        service = MonitorService()
        success = service.update_node("invalid_node", "active")

        assert success is False
        assert service.current_node is None
        assert len(service.event_log) == 0

    def test_node_deactivation(self):
        service = MonitorService()
        service.update_node("jira", "active")
        service.update_node("claude", "active")

        assert service.current_node == "claude"
        assert service.nodes["jira"].active is False
        assert service.nodes["claude"].active is True

    def test_event_log_limit(self):
        service = MonitorService(max_events=2)
        service.update_node("jira", "active", "1")
        service.update_node("claude", "active", "2")
        service.update_node("github", "active", "3")

        assert len(service.event_log) == 2
        assert service.event_log[0]["message"] == "2"
        assert service.event_log[1]["message"] == "3"

    def test_reset(self):
        service = MonitorService()
        service.update_node("jira", "active")
        service.set_task_info("Task 1", "running")

        service.reset()

        assert service.current_node is None
        assert len(service.event_log) == 0
        assert service.task_info["title"] == "Waiting for task..."

    def test_task_info(self):
        service = MonitorService()
        service.set_task_info("My Task", "running", "2024-01-01T00:00:00Z")

        info = service.get_task_info()
        assert info["title"] == "My Task"
        assert info["status"] == "running"
        assert info["start_time"] == "2024-01-01T00:00:00Z"

    def test_get_state(self):
        service = MonitorService()
        service.update_node("jira", "active")

        state = service.get_state()
        assert state["current_node"] == "jira"
        assert "nodes" in state
        assert "event_log" in state
        assert "task_info" in state
