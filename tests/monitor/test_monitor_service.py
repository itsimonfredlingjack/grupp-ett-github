"""Unit tests for MonitorService."""

import unittest
from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorService(unittest.TestCase):
    def setUp(self):
        self.service = MonitorService()

    def test_init(self):
        self.assertEqual(len(self.service.nodes), 5)
        self.assertIn("claude", self.service.nodes)
        self.assertEqual(len(self.service.event_log), 0)

    def test_update_node_valid(self):
        result = self.service.update_node("claude", "active", "Thinking...")
        self.assertTrue(result)
        self.assertTrue(self.service.nodes["claude"].active)
        self.assertEqual(self.service.nodes["claude"].message, "Thinking...")
        self.assertEqual(self.service.current_node, "claude")
        self.assertEqual(len(self.service.event_log), 1)

    def test_update_node_invalid(self):
        result = self.service.update_node("invalid_node", "active")
        self.assertFalse(result)

    def test_update_node_switch(self):
        self.service.update_node("claude", "active")
        self.assertTrue(self.service.nodes["claude"].active)

        self.service.update_node("jira", "active")
        self.assertFalse(self.service.nodes["claude"].active)
        self.assertTrue(self.service.nodes["jira"].active)
        self.assertEqual(self.service.current_node, "jira")

    def test_get_state(self):
        self.service.update_node("claude", "active", "Msg")
        state = self.service.get_state()
        self.assertEqual(state["current_node"], "claude")
        self.assertIn("nodes", state)
        self.assertIn("event_log", state)
        self.assertIn("task_info", state)

    def test_reset(self):
        self.service.update_node("claude", "active")
        self.service.reset()
        self.assertIsNone(self.service.current_node)
        self.assertFalse(self.service.nodes["claude"].active)
        self.assertEqual(len(self.service.event_log), 0)

    def test_set_task_info(self):
        self.service.set_task_info("New Task", "running", "2023-01-01T00:00:00Z")
        self.assertEqual(self.service.task_info["title"], "New Task")
        self.assertEqual(self.service.task_info["status"], "running")
        self.assertEqual(self.service.task_info["start_time"], "2023-01-01T00:00:00Z")

    def test_get_task_info(self):
        self.service.set_task_info("Task 1")
        info = self.service.get_task_info()
        self.assertEqual(info["title"], "Task 1")

    def test_log_rotation(self):
        service = MonitorService(max_events=2)
        service.add_event("claude", "1")
        service.add_event("claude", "2")
        service.add_event("claude", "3")
        self.assertEqual(len(service.event_log), 2)
        self.assertEqual(service.event_log[0]["message"], "2")
        self.assertEqual(service.event_log[1]["message"], "3")
