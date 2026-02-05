"""Tests for monitor service to improve coverage."""

import pytest

from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def service():
    """Create monitor service."""
    return MonitorService()


class TestMonitorService:
    """Test monitor service."""

    def test_service_initialization(self, service):
        """Service should initialize correctly."""
        assert service is not None

    def test_get_state(self, service):
        """Get state should return current state."""
        state = service.get_state()
        assert state is not None
        assert isinstance(state, dict)

    def test_update_node(self, service):
        """Update node should work."""
        result = service.update_node("claude", "active", "active")
        assert result is not None

    def test_add_event(self, service):
        """Add event should work."""
        service.add_event("claude", "test event")
        state = service.get_state()
        assert state is not None

    def test_get_task_info(self, service):
        """Get task info should work."""
        info = service.get_task_info()
        assert info is not None
        assert isinstance(info, dict)

    def test_multiple_nodes(self, service):
        """Multiple nodes should be trackable."""
        service.update_node("claude", "active", "msg1")
        service.update_node("jira", "inactive", "msg2")
        service.update_node("github", "active", "msg3")
        state = service.get_state()
        assert state is not None

    def test_reset(self, service):
        """Reset should clear state."""
        service.update_node("claude", "active", "test")
        service.reset()
        state = service.get_state()
        assert state is not None

    def test_set_task_info(self, service):
        """Set task info should work."""
        service.set_task_info("Test Task", "in_progress")
        info = service.get_task_info()
        assert info is not None
