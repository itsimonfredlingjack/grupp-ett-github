import pytest
from src.sejfa.monitor.monitor_service import MonitorService

@pytest.fixture
def monitor_service():
    return MonitorService()

def test_monitor_service_initialization(monitor_service):
    state = monitor_service.get_state()
    assert state["current_node"] is None
    assert len(state["nodes"]) == 5  # jira, claude, github, jules, actions
    assert len(state["event_log"]) == 0
    assert state["task_info"]["status"] == "idle"

def test_update_node_valid(monitor_service):
    success = monitor_service.update_node("claude", "active", "Coding...")
    assert success is True
    state = monitor_service.get_state()
    assert state["current_node"] == "claude"
    assert state["nodes"]["claude"]["active"] is True
    assert state["nodes"]["claude"]["message"] == "Coding..."
    assert len(state["event_log"]) == 1

def test_update_node_invalid(monitor_service):
    success = monitor_service.update_node("invalid_node", "active")
    assert success is False
    state = monitor_service.get_state()
    assert state["current_node"] is None

def test_update_node_deactivates_others(monitor_service):
    monitor_service.update_node("jira", "active")
    monitor_service.update_node("claude", "active")

    state = monitor_service.get_state()
    assert state["current_node"] == "claude"
    assert state["nodes"]["claude"]["active"] is True
    assert state["nodes"]["jira"]["active"] is False

def test_reset(monitor_service):
    monitor_service.update_node("claude", "active", "foo")
    monitor_service.reset()

    state = monitor_service.get_state()
    assert state["current_node"] is None
    assert state["nodes"]["claude"]["active"] is False
    assert len(state["event_log"]) == 0

def test_set_task_info(monitor_service):
    monitor_service.set_task_info("My Task", "running", "2023-01-01T00:00:00Z")
    task = monitor_service.get_task_info()
    assert task["title"] == "My Task"
    assert task["status"] == "running"
    assert task["start_time"] == "2023-01-01T00:00:00Z"
