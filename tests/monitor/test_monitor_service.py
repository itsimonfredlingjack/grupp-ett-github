from src.sejfa.monitor.monitor_service import MonitorService


def test_initial_state():
    service = MonitorService()
    state = service.get_state()
    assert state["current_node"] is None
    assert len(state["event_log"]) == 0
    assert state["task_info"]["status"] == "idle"


def test_update_node_valid():
    service = MonitorService()
    service.update_node("claude", "active", "Thinking...")
    state = service.get_state()
    assert state["current_node"] == "claude"
    assert state["nodes"]["claude"]["active"] is True
    assert len(state["event_log"]) == 1
    assert state["event_log"][0]["node"] == "claude"


def test_update_node_invalid():
    service = MonitorService()
    result = service.update_node("invalid_node", "active")
    assert result is False
    assert service.get_state()["current_node"] is None


def test_reset():
    service = MonitorService()
    service.update_node("claude", "active")
    service.reset()
    state = service.get_state()
    assert state["current_node"] is None
    assert len(state["event_log"]) == 0


def test_task_info():
    service = MonitorService()
    service.set_task_info("Test Task", "running", "2023-01-01T00:00:00Z")
    info = service.get_task_info()
    assert info["title"] == "Test Task"
    assert info["status"] == "running"
    assert info["start_time"] == "2023-01-01T00:00:00Z"
