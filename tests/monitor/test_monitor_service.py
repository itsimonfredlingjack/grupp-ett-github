import pytest

from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def monitor_service():
    return MonitorService()


def test_initial_state(monitor_service):
    assert "jira" in monitor_service.nodes
    assert "claude" in monitor_service.nodes
    assert "github" in monitor_service.nodes
    assert "jules" in monitor_service.nodes
    assert "actions" in monitor_service.nodes
    assert monitor_service.event_log == []


def test_update_node_adds_node(monitor_service):
    result = monitor_service.update_node("jules", "active", "Test message")
    assert result is True
    assert monitor_service.nodes["jules"].active is True
    assert monitor_service.nodes["jules"].message == "Test message"


def test_update_node_invalid_node(monitor_service):
    result = monitor_service.update_node("invalid_node", "active", "Test message")
    assert result is False
    assert "invalid_node" not in monitor_service.nodes


def test_update_node_updates_existing_node(monitor_service):
    monitor_service.update_node("jules", "active", "First message")
    monitor_service.update_node("jules", "idle", "Second message")
    assert monitor_service.nodes["jules"].active is False
    assert monitor_service.nodes["jules"].message == "Second message"


def test_update_node_adds_event_to_log(monitor_service):
    monitor_service.update_node("jules", "active", "Test message")
    assert len(monitor_service.event_log) == 1
    event = monitor_service.event_log[0]
    assert event["node"] == "jules"
    assert event["message"] == "Test message"


def test_get_state_returns_correct_structure(monitor_service):
    monitor_service.update_node("jules", "active", "Test message")
    state = monitor_service.get_state()
    assert "nodes" in state
    assert "event_log" in state
    assert state["nodes"]["jules"]["active"] is True
    assert len(state["event_log"]) == 1


def test_get_state_returns_copy(monitor_service):
    state = monitor_service.get_state()
    state["nodes"]["new_node"] = {}
    assert "new_node" not in monitor_service.nodes


def test_update_node_handles_none_message(monitor_service):
    monitor_service.update_node("jules", "active", "")
    assert monitor_service.nodes["jules"].message == ""


def test_reset(monitor_service):
    monitor_service.update_node("jules", "active", "Test")
    monitor_service.reset()
    assert monitor_service.nodes["jules"].active is False
    assert len(monitor_service.event_log) == 0
    assert monitor_service.current_node is None


def test_set_task_info(monitor_service):
    monitor_service.set_task_info(title="Task", status="running")
    info = monitor_service.get_task_info()
    assert info["title"] == "Task"
    assert info["status"] == "running"
