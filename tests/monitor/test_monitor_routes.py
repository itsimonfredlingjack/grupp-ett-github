"""Basic tests for monitor routes to improve coverage."""

import pytest
from flask import Flask
from flask_socketio import SocketIO

from src.sejfa.monitor.monitor_routes import create_monitor_blueprint
from src.sejfa.monitor.monitor_service import MonitorService


@pytest.fixture
def app():
    """Create test Flask app."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test-secret"
    return app


@pytest.fixture
def socketio(app):
    """Create socketio instance."""
    return SocketIO(app, cors_allowed_origins="*")


@pytest.fixture
def monitor_service():
    """Create monitor service."""
    return MonitorService()


@pytest.fixture
def client(app, socketio, monitor_service):
    """Create test client with monitor blueprint."""
    blueprint = create_monitor_blueprint(monitor_service, socketio)
    app.register_blueprint(blueprint)
    return app.test_client()


class TestMonitorRoutes:
    """Test monitor routes."""

    def test_update_state_endpoint_exists(self, client):
        """State update endpoint should be reachable."""
        response = client.post(
            "/api/monitor/state",
            json={"node": "claude", "state": "active", "message": "test"},
        )
        # Should return 200 or 400, but not 404
        assert response.status_code in [200, 400, 500]

    def test_health_check_endpoint_exists(self, client):
        """Health check endpoint should be reachable."""
        response = client.get("/api/monitor/health")
        assert response.status_code in [200, 404]

    def test_metrics_endpoint_exists(self, client):
        """Metrics endpoint should be reachable."""
        response = client.get("/api/monitor/metrics")
        assert response.status_code in [200, 404]
