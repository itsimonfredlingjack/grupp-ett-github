from src.sejfa.monitor.monitor_service import MonitorService


def test_monitor_service_initialization():
    service = MonitorService(max_events=50)
    assert service.max_events == 50
    assert service.current_node is None
    assert len(service.event_log) == 0
    assert "claude" in service.nodes

def test_update_node_valid():
    service = MonitorService()
    result = service.update_node("claude", "active", "Thinking...")
    assert result is True
    assert service.current_node == "claude"
    assert service.nodes["claude"].active is True
    assert service.nodes["claude"].message == "Thinking..."
    assert len(service.event_log) == 1

def test_update_node_invalid():
    service = MonitorService()
    result = service.update_node("invalid_node", "active")
    assert result is False
    assert len(service.event_log) == 0

def test_update_node_deactivates_previous():
    service = MonitorService()
    service.update_node("jira", "active")
    assert service.nodes["jira"].active is True

    service.update_node("claude", "active")
    assert service.nodes["jira"].active is False
    assert service.nodes["claude"].active is True
    assert service.current_node == "claude"

def test_get_state():
    service = MonitorService()
    service.update_node("github", "active", "Pushing code")
    state = service.get_state()

    assert state["current_node"] == "github"
    assert state["nodes"]["github"]["active"] is True
    assert len(state["event_log"]) == 1
    assert state["task_info"]["status"] == "idle"

def test_reset():
    service = MonitorService()
    service.update_node("jules", "active")
    service.set_task_info("Test Task", "running")

    service.reset()

    assert service.current_node is None
    assert len(service.event_log) == 0
    assert service.task_info["status"] == "idle"
    assert service.nodes["jules"].active is False

def test_set_task_info():
    service = MonitorService()
    service.set_task_info("Fix Bug", "running", "2023-01-01T12:00:00Z")

    info = service.get_task_info()
    assert info["title"] == "Fix Bug"
    assert info["status"] == "running"
    assert info["start_time"] == "2023-01-01T12:00:00Z"

def test_event_log_truncation():
    service = MonitorService(max_events=5)
    for i in range(10):
        service.add_event("jira", f"Message {i}")

    assert len(service.event_log) == 5
    assert service.event_log[-1]["message"] == "Message 9"
