"""Tests for the MonitorService class."""

from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    """Tests for MonitorService functionality."""

    def test_initialization(self) -> None:
        """Test initial state of MonitorService."""
        service = MonitorService()
        state = service.get_state()

        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"
        assert len(state["nodes"]) == 5  # jira, claude, github, jules, actions

    def test_update_node_valid(self) -> None:
        """Test updating a valid node."""
        service = MonitorService()
        success = service.update_node("claude", "active", "Coding...")

        assert success is True
        state = service.get_state()
        assert state["current_node"] == "claude"
        assert state["nodes"]["claude"]["active"] is True
        assert state["nodes"]["claude"]["message"] == "Coding..."
        assert len(state["event_log"]) == 1
        assert state["event_log"][0]["node"] == "claude"
        assert state["event_log"][0]["message"] == "Coding..."

    def test_update_node_invalid(self) -> None:
        """Test updating an invalid node."""
        service = MonitorService()
        success = service.update_node("invalid_node", "active")

        assert success is False
        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0

    def test_update_node_transitions(self) -> None:
        """Test transitioning between nodes."""
        service = MonitorService()

        # Activate first node
        service.update_node("jira", "active", "Fetching")
        assert service.current_node == "jira"
        assert service.nodes["jira"].active is True

        # Activate second node
        service.update_node("claude", "active", "Thinking")
        assert service.current_node == "claude"
        assert service.nodes["claude"].active is True
        # Previous node should be deactivated
        assert service.nodes["jira"].active is False

    def test_reset(self) -> None:
        """Test resetting the service."""
        service = MonitorService()
        service.update_node("claude", "active", "Coding")
        service.set_task_info("Test Task", "running")

        service.reset()
        state = service.get_state()

        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"
        assert state["nodes"]["claude"]["active"] is False

    def test_task_info(self) -> None:
        """Test updating task information."""
        service = MonitorService()
        service.set_task_info("New Task", "running", "2023-01-01T00:00:00Z")

        info = service.get_task_info()
        assert info["title"] == "New Task"
        assert info["status"] == "running"
        assert info["start_time"] == "2023-01-01T00:00:00Z"

    def test_event_log_limit(self) -> None:
        """Test that event log respects max_events."""
        service = MonitorService(max_events=3)
        for i in range(5):
            service.add_event("claude", f"Message {i}")

        state = service.get_state()
        assert len(state["event_log"]) == 3
        assert state["event_log"][-1]["message"] == "Message 4"
        assert state["event_log"][0]["message"] == "Message 2"
