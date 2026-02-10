from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService:
    def test_init(self):
        service = MonitorService()
        # Verify default nodes exist
        assert "actions" in service.nodes
        assert "claude" in service.nodes
        assert service.event_log == []

    def test_update_node_valid(self):
        service = MonitorService()
        node_id = "claude"

        # Act
        result = service.update_node(node_id, "active", "Processing...")

        # Assert
        assert result is True
        assert service.nodes[node_id].active is True
        assert service.nodes[node_id].message == "Processing..."
        assert service.current_node == node_id
        assert len(service.event_log) == 1

    def test_update_node_invalid(self):
        service = MonitorService()
        result = service.update_node("invalid_node", "active")
        assert result is False

    def test_update_node_switching(self):
        service = MonitorService()

        # Activate first node
        service.update_node("claude", "active")
        assert service.nodes["claude"].active is True

        # Activate second node
        service.update_node("jira", "active")

        # Assert switch
        assert service.nodes["claude"].active is False
        assert service.nodes["jira"].active is True
        assert service.current_node == "jira"

    def test_add_event_limit(self):
        service = MonitorService(max_events=5)
        for i in range(10):
            service.add_event("claude", f"msg{i}")

        assert len(service.event_log) == 5
        assert service.event_log[-1]["message"] == "msg9"

    def test_reset(self):
        service = MonitorService()
        service.update_node("claude", "active")
        service.set_task_info("Title", "running")

        service.reset()

        assert service.current_node is None
        assert service.event_log == []
        assert service.task_info["status"] == "idle"
        # Nodes should be reset (inactive)
        assert service.nodes["claude"].active is False

    def test_set_task_info(self):
        service = MonitorService()
        service.set_task_info("New Task", "running", "2023-01-01T00:00:00Z")

        info = service.get_task_info()
        assert info["title"] == "New Task"
        assert info["status"] == "running"
        assert info["start_time"] == "2023-01-01T00:00:00Z"

    def test_get_state(self):
        service = MonitorService()
        service.update_node("claude", "active")

        state = service.get_state()
        assert state["current_node"] == "claude"
        assert "nodes" in state
        assert "event_log" in state
        assert "task_info" in state
