import pytest
from src.sejfa.monitor.monitor_service import MonitorService

class TestMonitorService:
    def test_init(self):
        service = MonitorService()
        assert service.current_node is None
        assert len(service.nodes) == 5
        assert len(service.event_log) == 0
        assert service.task_info["status"] == "idle"

    def test_update_node_valid(self):
        service = MonitorService()
        result = service.update_node("claude", "active", "Writing code")
        assert result is True
        assert service.current_node == "claude"
        assert service.nodes["claude"].active is True
        assert service.nodes["claude"].message == "Writing code"
        assert len(service.event_log) == 1

    def test_update_node_invalid(self):
        service = MonitorService()
        result = service.update_node("invalid_node", "active")
        assert result is False
        assert len(service.event_log) == 0

    def test_update_node_deactivates_previous(self):
        service = MonitorService()
        service.update_node("claude", "active")
        assert service.nodes["claude"].active is True

        service.update_node("actions", "active")
        assert service.nodes["claude"].active is False
        assert service.nodes["actions"].active is True
        assert service.current_node == "actions"

    def test_get_state(self):
        service = MonitorService()
        service.update_node("claude", "active", "test")
        state = service.get_state()
        assert state["current_node"] == "claude"
        assert "nodes" in state
        assert "event_log" in state
        assert "task_info" in state

    def test_reset(self):
        service = MonitorService()
        service.update_node("claude", "active")
        service.set_task_info("Test Task", "running")

        service.reset()
        assert service.current_node is None
        assert len(service.event_log) == 0
        assert service.task_info["status"] == "idle"
        assert service.nodes["claude"].active is False

    def test_set_task_info(self):
        service = MonitorService()
        service.set_task_info("New Task", "running", "2023-01-01T00:00:00Z")
        assert service.task_info["title"] == "New Task"
        assert service.task_info["status"] == "running"
        assert service.task_info["start_time"] == "2023-01-01T00:00:00Z"

    def test_get_task_info(self):
        service = MonitorService()
        service.set_task_info("Task A")
        info = service.get_task_info()
        assert info["title"] == "Task A"
        # Verify it returns a copy
        info["title"] = "Modified"
        assert service.task_info["title"] == "Task A"

    def test_event_log_limit(self):
        service = MonitorService(max_events=2)
        service.add_event("jira", "1")
        service.add_event("claude", "2")
        service.add_event("github", "3")

        assert len(service.event_log) == 2
        assert service.event_log[0]["message"] == "2"
        assert service.event_log[1]["message"] == "3"
