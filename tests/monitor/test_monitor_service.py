import pytest

from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def monitor_service():
    return MonitorService(max_events=10)


class TestMonitorService:
    def test_initialization(self, monitor_service):
        assert monitor_service.current_node is None
        assert len(monitor_service.nodes) == 5
        assert monitor_service.event_log == []
        assert monitor_service.task_info["status"] == "idle"

    def test_update_node_valid(self, monitor_service):
        # Activate a node
        success = monitor_service.update_node("claude", "active", "Processing request")
        assert success is True
        assert monitor_service.current_node == "claude"
        assert monitor_service.nodes["claude"].active is True
        assert monitor_service.nodes["claude"].message == "Processing request"
        assert len(monitor_service.event_log) == 1
        assert monitor_service.event_log[0]["node"] == "claude"

        # Switch to another node
        monitor_service.update_node("jira", "active", "Checking ticket")
        assert monitor_service.current_node == "jira"
        assert monitor_service.nodes["claude"].active is False
        assert monitor_service.nodes["jira"].active is True
        assert len(monitor_service.event_log) == 2

    def test_update_node_invalid(self, monitor_service):
        success = monitor_service.update_node("invalid_node", "active")
        assert success is False
        assert len(monitor_service.event_log) == 0

    def test_update_node_inactive(self, monitor_service):
        monitor_service.update_node("claude", "active")
        assert monitor_service.nodes["claude"].active is True

        monitor_service.update_node("claude", "inactive")
        assert monitor_service.nodes["claude"].active is False
        # Note: In current implementation, deactivating doesn't clear current_node
        # if it was the active one, but the node itself is marked inactive.

    def test_log_size_limit(self, monitor_service):
        # max_events is 10
        for i in range(15):
            monitor_service.add_event("claude", f"Message {i}")

        assert len(monitor_service.event_log) == 10
        assert monitor_service.event_log[0]["message"] == "Message 5"
        assert monitor_service.event_log[-1]["message"] == "Message 14"

    def test_get_state(self, monitor_service):
        monitor_service.update_node("claude", "active", "Test")
        state = monitor_service.get_state()

        assert "current_node" in state
        assert "nodes" in state
        assert "event_log" in state
        assert "task_info" in state
        assert state["current_node"] == "claude"
        assert state["nodes"]["claude"]["active"] is True

    def test_reset(self, monitor_service):
        monitor_service.update_node("claude", "active")
        monitor_service.set_task_info("Task 1", "running")

        monitor_service.reset()

        assert monitor_service.current_node is None
        assert len(monitor_service.event_log) == 0
        assert monitor_service.task_info["status"] == "idle"
        assert monitor_service.nodes["claude"].active is False

    def test_task_info(self, monitor_service):
        monitor_service.set_task_info("Fix bug", "running", "2023-01-01T12:00:00Z")
        info = monitor_service.get_task_info()

        assert info["title"] == "Fix bug"
        assert info["status"] == "running"
        assert info["start_time"] == "2023-01-01T12:00:00Z"

        # Test partial update
        monitor_service.set_task_info(status="completed")
        assert monitor_service.task_info["title"] == "Fix bug"
        assert monitor_service.task_info["status"] == "completed"
