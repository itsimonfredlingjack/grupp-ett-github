"""Unit tests for MonitorService."""

from datetime import datetime

from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    """Tests for MonitorService class."""

    def test_initialization(self):
        """Test initial state of service."""
        service = MonitorService()
        state = service.get_state()

        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"
        assert len(state["nodes"]) == 5
        assert "jira" in state["nodes"]

    def test_update_node_valid(self):
        """Test updating a valid node."""
        service = MonitorService()
        result = service.update_node("jira", "active", "Fetching ticket")

        assert result is True
        state = service.get_state()
        assert state["current_node"] == "jira"
        assert state["nodes"]["jira"]["active"] is True
        assert state["nodes"]["jira"]["message"] == "Fetching ticket"
        assert len(state["event_log"]) == 1
        assert state["event_log"][0]["node"] == "jira"

    def test_update_node_invalid(self):
        """Test updating an invalid node."""
        service = MonitorService()
        result = service.update_node("invalid_node", "active")

        assert result is False
        assert service.current_node is None

    def test_node_transition(self):
        """Test transition between nodes."""
        service = MonitorService()

        # Activate first node
        service.update_node("jira", "active")
        assert service.nodes["jira"].active is True

        # Activate second node
        service.update_node("claude", "active")

        # First should be inactive, second active
        assert service.nodes["jira"].active is False
        assert service.nodes["claude"].active is True
        assert service.current_node == "claude"

    def test_event_log_limit(self):
        """Test that event log respects max_events."""
        service = MonitorService(max_events=5)

        for i in range(10):
            service.add_event("jira", f"Message {i}")

        state = service.get_state()
        assert len(state["event_log"]) == 5
        assert state["event_log"][-1]["message"] == "Message 9"

    def test_reset(self):
        """Test resetting the service."""
        service = MonitorService()
        service.update_node("jira", "active")
        service.set_task_info("Task 1", "running")

        service.reset()

        state = service.get_state()
        assert state["current_node"] is None
        assert len(state["event_log"]) == 0
        assert state["task_info"]["status"] == "idle"
        assert all(not n["active"] for n in state["nodes"].values())

    def test_task_info(self):
        """Test updating task info."""
        service = MonitorService()
        start_time = datetime.utcnow().isoformat() + "Z"

        service.set_task_info("New Task", "running", start_time)

        info = service.get_task_info()
        assert info["title"] == "New Task"
        assert info["status"] == "running"
        assert info["start_time"] == start_time

    def test_update_node_truncates_message(self):
        """Test that long messages are truncated."""
        service = MonitorService()
        long_message = "a" * 300
        service.update_node("jira", "active", long_message)

        state = service.get_state()
        assert len(state["nodes"]["jira"]["message"]) == 200
        assert len(state["event_log"][0]["message"]) == 200
