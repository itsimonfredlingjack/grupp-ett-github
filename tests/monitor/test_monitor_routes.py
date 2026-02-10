"""Unit tests for Monitor Routes."""

import unittest
from unittest.mock import MagicMock
from flask import Flask
from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


class TestMonitorRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.monitor_service = MonitorService()
        self.socketio = MagicMock()

        self.blueprint = create_monitor_blueprint(self.monitor_service, self.socketio)
        self.app.register_blueprint(self.blueprint)
        self.client = self.app.test_client()

    def test_get_state(self):
        response = self.client.get("/api/monitor/state")
        self.assertEqual(response.status_code, 200)
        self.assertIn("current_node", response.json)

    def test_update_state_success(self):
        response = self.client.post("/api/monitor/state", json={
            "node": "claude",
            "state": "active",
            "message": "Working"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["success"])
        self.assertEqual(self.monitor_service.current_node, "claude")
        self.socketio.emit.assert_called()

    def test_update_state_invalid_node(self):
        response = self.client.post("/api/monitor/state", json={
            "node": "invalid",
            "state": "active"
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json["success"])

    def test_update_state_no_json(self):
        response = self.client.post("/api/monitor/state")
        self.assertEqual(response.status_code, 400)

    def test_reset_monitoring(self):
        self.monitor_service.update_node("claude", "active")
        response = self.client.post("/api/monitor/reset")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["success"])
        self.assertIsNone(self.monitor_service.current_node)

    def test_update_task(self):
        response = self.client.post("/api/monitor/task", json={
            "title": "My Task",
            "status": "running"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.monitor_service.task_info["title"], "My Task")
        self.assertEqual(self.monitor_service.task_info["status"], "running")

    def test_update_task_no_json(self):
        response = self.client.post("/api/monitor/task")
        self.assertEqual(response.status_code, 400)
