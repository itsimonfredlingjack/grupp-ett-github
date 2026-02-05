"""Integration tests for Cursorflash with main Flask app."""

import json

import pytest

from app import create_app


@pytest.fixture
def app():
    """Create test Flask application."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestCursorflashIntegration:
    """Tests for Cursorflash integration in main app."""

    def test_cursorflash_routes_available(self, client):
        """Test that cursorflash routes are registered in main app."""
        response = client.get("/cursorflash/")
        assert response.status_code == 200

    def test_cursorflash_add_works_in_main_app(self, client):
        """Test that adding flash works through main app."""
        response = client.post(
            "/cursorflash/add",
            json={
                "title": "Integration Test Flash",
                "content": "This is content for integration test.",
                "author": "Integration Tester",
            },
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["title"] == "Integration Test Flash"

    def test_cursorflash_update_works_in_main_app(self, client):
        """Test that updating flash works through main app."""
        # Create first
        create_response = client.post(
            "/cursorflash/add",
            json={
                "title": "Original Title",
                "content": "Original content here",
                "author": "Test Author",
            },
        )
        flash_id = json.loads(create_response.data)["id"]

        # Update
        response = client.put(
            f"/cursorflash/update/{flash_id}",
            json={
                "title": "Updated Title",
            },
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["title"] == "Updated Title"

    def test_existing_routes_still_work(self, client):
        """Test that existing app routes still work after integration."""
        # Test root route
        response = client.get("/")
        assert response.status_code == 200

        # Test health route
        response = client.get("/health")
        assert response.status_code == 200
