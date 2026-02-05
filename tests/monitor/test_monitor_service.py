"""Tests for MonitorService."""

import tempfile
from pathlib import Path

from src.sejfa.monitor.monitor_service import Event, MonitorService, STEPS


class TestMonitorService:
    """Tests for the MonitorService class."""

    def setup_method(self):
        """Reset the singleton instance before each test."""
        MonitorService._instance = None
        self.service = MonitorService()

    def test_singleton_pattern(self):
        """MonitorService should be a singleton."""
        service1 = MonitorService()
        service2 = MonitorService()
        assert service1 is service2

    def test_initial_state(self):
        """Service should start in idle state."""
        state = self.service.get_state()

        assert state["status"] == "idle"
        assert state["task"] is None
        assert state["events"] == []
        assert state["elapsed_seconds"] == 0

    def test_start_task(self):
        """Starting a task should update state correctly."""
        result = self.service.start_task(
            task_id="GE-123",
            title="Test Task",
            branch="feature/GE-123-test",
            max_iterations=10,
        )

        assert result["task_id"] == "GE-123"
        assert result["title"] == "Test Task"
        assert result["step"] == 0
        assert result["status"] == "in_progress"
        assert result["max_iterations"] == 10

        state = self.service.get_state()
        assert state["status"] == "running"

    def test_update_task_step(self):
        """Updating task step should work correctly."""
        self.service.start_task("GE-123")

        result = self.service.update_task(
            step=1,
            step_name="Custom Name",
            step_desc="Custom Description",
        )

        assert result["step"] == 1
        assert result["step_name"] == "Custom Name"
        assert result["step_desc"] == "Custom Description"

    def test_update_task_iteration(self):
        """Updating iteration count should work."""
        self.service.start_task("GE-123")

        result = self.service.update_task(iteration=5)

        assert result["iteration"] == 5

    def test_complete_task(self):
        """Completing a task should set status to done."""
        self.service.start_task("GE-123")

        result = self.service.complete_task()

        assert result["status"] == "done"
        assert result["step"] == 4  # Last step (CI Pipeline)

        state = self.service.get_state()
        assert state["status"] == "idle"

    def test_fail_task(self):
        """Failing a task should set status to failed."""
        self.service.start_task("GE-123")

        result = self.service.fail_task("Tests failed")

        assert result["status"] == "failed"
        assert result["step_desc"] == "Tests failed"

    def test_reset(self):
        """Reset should clear all state."""
        self.service.start_task("GE-123")
        self.service.add_event("info", "Test event")

        self.service.reset()

        state = self.service.get_state()
        assert state["status"] == "idle"
        assert state["task"] is None
        assert state["events"] == []

    def test_add_event(self):
        """Adding events should work correctly."""
        event = self.service.add_event(
            event_type="info",
            message="Test message",
            source="test",
        )

        assert event.event_type == "info"
        assert event.message == "Test message"
        assert event.source == "test"

        events = self.service.get_events()
        assert len(events) == 1
        assert events[0]["message"] == "Test message"

    def test_event_limit(self):
        """Events should be limited to 100."""
        for i in range(150):
            self.service.add_event("info", f"Event {i}")

        events = self.service.get_events(limit=200)
        # Should only keep last 100
        assert len(events) <= 100

    def test_event_to_dict(self):
        """Event should serialize correctly."""
        event = Event(
            event_type="success",
            message="Task completed",
            source="monitor",
            task_id="GE-123",
            metadata={"key": "value"},
        )

        data = event.to_dict()

        assert data["event_type"] == "success"
        assert data["message"] == "Task completed"
        assert data["source"] == "monitor"
        assert data["task_id"] == "GE-123"
        assert data["metadata"] == {"key": "value"}
        assert "timestamp" in data


class TestToolToStepMapping:
    """Tests for tool-to-step mapping."""

    def test_read_tool_maps_to_jira(self):
        """Read tool should map to Jira step (0)."""
        step, desc = MonitorService.tool_to_step("Read")
        assert step == 0
        assert "Reading" in desc

    def test_edit_tool_maps_to_claude(self):
        """Edit tool should map to Claude step (1)."""
        step, desc = MonitorService.tool_to_step("Edit")
        assert step == 1
        assert "Editing" in desc

    def test_git_commit_maps_to_github(self):
        """git commit should map to GitHub step (2)."""
        step, desc = MonitorService.tool_to_step("git commit")
        assert step == 2
        assert "Committing" in desc

    def test_bash_maps_to_actions(self):
        """Bash tool should map to Actions step (4)."""
        step, desc = MonitorService.tool_to_step("Bash")
        assert step == 4

    def test_unknown_tool_defaults_to_claude(self):
        """Unknown tools should default to Claude step."""
        step, desc = MonitorService.tool_to_step("UnknownTool")
        assert step == 1


class TestParseCurrentTask:
    """Tests for CURRENT_TASK.md parsing."""

    def test_parse_nonexistent_file(self):
        """Parsing nonexistent file should return None."""
        service = MonitorService()
        result = service.parse_current_task("/nonexistent/path.md")
        assert result is None

    def test_parse_task_file(self):
        """Should extract iteration and criteria from task file."""
        service = MonitorService()

        # Create a temporary task file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("""# Current Task: GE-123

## Progress
Iteration: 5

## Acceptance Criteria
- [x] First criterion
- [x] Second criterion
- [ ] Third criterion
- [ ] Fourth criterion
""")
            task_path = f.name

        try:
            result = service.parse_current_task(task_path)

            assert result is not None
            assert result["active"] is True
            assert result["iteration"] == 5
            assert result["criteria_checked"] == 2
            assert result["criteria_total"] == 4
            assert result["task_id"] == "GE-123"
        finally:
            Path(task_path).unlink()

    def test_parse_task_extracts_task_id(self):
        """Should extract Jira-style task ID."""
        service = MonitorService()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Working on PROJ-456\nSome content")
            task_path = f.name

        try:
            result = service.parse_current_task(task_path)
            assert result["task_id"] == "PROJ-456"
        finally:
            Path(task_path).unlink()


class TestStepsConstant:
    """Tests for the STEPS constant."""

    def test_steps_has_correct_count(self):
        """Should have exactly 5 visual workflow steps."""
        assert len(STEPS) == 5

    def test_each_step_has_required_fields(self):
        """Each step should have name and desc."""
        for step in STEPS:
            assert "name" in step
            assert "desc" in step
