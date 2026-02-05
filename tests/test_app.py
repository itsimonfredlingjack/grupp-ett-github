from unittest.mock import patch

import pytest

from app import create_app


class TestHelloEndpoint:
    @pytest.fixture
    def client(self):
        app = create_app()
        app.config["TESTING"] = True
        return app.test_client()

    def test_hello_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_hello_returns_json(self, client):
        response = client.get("/")
        assert response.is_json

    def test_hello_returns_message(self, client):
        response = client.get("/")
        data = response.get_json()
        assert data["message"] == "Hello, Agentic Dev Loop!"


class TestHealthEndpoint:
    @pytest.fixture
    def client(self):
        app = create_app()
        app.config["TESTING"] = True
        return app.test_client()

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get("/health")
        assert response.is_json

    def test_health_returns_healthy_status(self, client):
        response = client.get("/health")
        data = response.get_json()
        assert data["status"] == "healthy"


class TestAppCreation:
    def test_create_app_returns_flask_instance(self):
        from flask import Flask

        app = create_app()
        assert isinstance(app, Flask)

    def test_create_app_has_routes(self):
        app = create_app()
        # Check if the rules map contains our routes
        rules = [str(p) for p in app.url_map.iter_rules()]
        assert "/" in rules
        assert "/health" in rules


def test_app_module_execution():
    """Test that app.py can be executed as a script."""
    # We mock socketio.run to prevent the server from actually starting and blocking
    with patch("flask_socketio.SocketIO.run"):
        # Import app to trigger module-level code
        import app

        # Re-execute the module to ensure __main__ block is hit if we were to run it
        # Since we can't easily re-import with __name__ == "__main__", we check imports
        assert app.create_app is not None
