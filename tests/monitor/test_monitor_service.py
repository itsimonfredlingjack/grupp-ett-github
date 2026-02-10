"""Tests for MonitorService."""

import pytest

from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def monitor_service():
    """Create a fresh MonitorService instance."""
    return MonitorService(max_events=5)


def test_initial_state(monitor_service):
    """Test initial state of the service."""
    state = monitor_service.get_state()
    assert state["current_node"] is None
    assert len(state["event_log"]) == 0
    assert state["task_info"]["status"] == "idle"

    for node_id in MonitorService.VALID_NODES:
        assert node_id in state["nodes"]
        assert not state["nodes"][node_id]["active"]


def test_update_node_valid(monitor_service):
    """Test updating a valid node."""
    success = monitor_service.update_node("claude", "active", "Thinking")
    assert success is True

    state = monitor_service.get_state()
    assert state["current_node"] == "claude"
    assert state["nodes"]["claude"]["active"] is True
    assert state["nodes"]["claude"]["message"] == "Thinking"
    assert len(state["event_log"]) == 1
    assert state["event_log"][0]["node"] == "claude"
    assert state["event_log"][0]["message"] == "Thinking"


def test_update_node_invalid(monitor_service):
    """Test updating an invalid node."""
    success = monitor_service.update_node("invalid_node", "active")
    assert success is False

    state = monitor_service.get_state()
    assert state["current_node"] is None
    assert len(state["event_log"]) == 0


def test_update_node_transition(monitor_service):
    """Test transitioning from one node to another."""
    monitor_service.update_node("claude", "active", "Start")
    monitor_service.update_node("github", "active", "Pushing")

    state = monitor_service.get_state()
    assert state["current_node"] == "github"
    assert state["nodes"]["github"]["active"] is True
    assert state["nodes"]["claude"]["active"] is False  # Should be deactivated
    assert len(state["event_log"]) == 2


def test_update_node_same_active(monitor_service):
    """Test updating the same node that is already active."""
    monitor_service.update_node("claude", "active", "First")
    monitor_service.update_node("claude", "active", "Second")

    state = monitor_service.get_state()
    assert state["current_node"] == "claude"
    assert state["nodes"]["claude"]["active"] is True
    assert len(state["event_log"]) == 2
    assert state["event_log"][1]["message"] == "Second"


def test_event_log_limit(monitor_service):
    """Test that event log respects max_events."""
    # max_events is set to 5 in fixture
    for i in range(10):
        monitor_service.update_node("claude", "active", f"Msg {i}")

    state = monitor_service.get_state()
    assert len(state["event_log"]) == 5
    assert state["event_log"][-1]["message"] == "Msg 9"
    assert state["event_log"][0]["message"] == "Msg 5"


def test_reset(monitor_service):
    """Test resetting the service."""
    monitor_service.update_node("claude", "active", "Start")
    monitor_service.set_task_info("Task 1", "running")

    monitor_service.reset()

    state = monitor_service.get_state()
    assert state["current_node"] is None
    assert len(state["event_log"]) == 0
    assert state["task_info"]["status"] == "idle"
    assert not state["nodes"]["claude"]["active"]


def test_set_task_info(monitor_service):
    """Test updating task info."""
    monitor_service.set_task_info("Fix Bug", "running", "2023-01-01T00:00:00Z")

    task_info = monitor_service.get_task_info()
    assert task_info["title"] == "Fix Bug"
    assert task_info["status"] == "running"
    assert task_info["start_time"] == "2023-01-01T00:00:00Z"


def test_set_task_info_partial(monitor_service):
    """Test partial updates to task info."""
    monitor_service.set_task_info(title="Task A")
    monitor_service.set_task_info(status="failed")

    task_info = monitor_service.get_task_info()
    assert task_info["title"] == "Task A"
    assert task_info["status"] == "failed"
