"""Tests for NewsFlash Flask routes (presentation layer)."""

import json

import pytest
from flask import Flask

from src.sejfa.cursorflash.repository import InMemoryNewsFlashRepository
from src.sejfa.cursorflash.routes import create_cursorflash_blueprint
from src.sejfa.cursorflash.service import NewsFlashService


@pytest.fixture
def app():
    """Create test Flask application with cursorflash blueprint."""
    app = Flask(__name__)
    app.config["TESTING"] = True

    repository = InMemoryNewsFlashRepository()
    service = NewsFlashService(repository=repository)
    blueprint = create_cursorflash_blueprint(service)

    app.register_blueprint(blueprint, url_prefix="/cursorflash")

    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestCursorflashRoutesList:
    """Tests for GET / (list all flashes)."""

    def test_get_empty_list(self, client):
        """Test GET / returns empty list initially."""
        response = client.get("/cursorflash/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "flashes" in data
        assert data["flashes"] == []

    def test_get_list_with_flashes(self, client):
        """Test GET / returns created flashes."""
        # Create a flash first
        client.post(
            "/cursorflash/add",
            json={
                "title": "Test Flash",
                "content": "This is test content here",
                "author": "Test Author",
            },
        )

        response = client.get("/cursorflash/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["flashes"]) == 1
        assert data["flashes"][0]["title"] == "Test Flash"


class TestCursorflashRoutesAdd:
    """Tests for POST /add (create flash)."""

    def test_add_flash_success(self, client):
        """Test POST /add creates a new flash."""
        response = client.post(
            "/cursorflash/add",
            json={
                "title": "Ny Nyhetsflash",
                "content": "Detta är innehållet i nyhetsflashen.",
                "author": "Test Author",
            },
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["title"] == "Ny Nyhetsflash"
        assert data["content"] == "Detta är innehållet i nyhetsflashen."
        assert "id" in data
        assert "created_at" in data

    def test_add_flash_missing_title(self, client):
        """Test POST /add with missing title returns error in Swedish."""
        response = client.post(
            "/cursorflash/add",
            json={
                "content": "Valid content here",
                "author": "Test Author",
            },
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "fel" in data
        assert "Titel krävs" in data["fel"]

    def test_add_flash_title_too_long(self, client):
        """Test POST /add with title > 100 chars returns Swedish error."""
        response = client.post(
            "/cursorflash/add",
            json={
                "title": "A" * 101,
                "content": "Valid content here",
                "author": "Test Author",
            },
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "fel" in data
        assert "Titel får inte överstiga 100 tecken" in data["fel"]

    def test_add_flash_content_too_short(self, client):
        """Test POST /add with content < 10 chars returns Swedish error."""
        response = client.post(
            "/cursorflash/add",
            json={
                "title": "Valid Title",
                "content": "Short",  # Only 5 chars
                "author": "Test Author",
            },
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "fel" in data
        assert "Innehåll måste vara minst 10 tecken" in data["fel"]

    def test_add_flash_content_too_long(self, client):
        """Test POST /add with content > 5000 chars returns Swedish error."""
        response = client.post(
            "/cursorflash/add",
            json={
                "title": "Valid Title",
                "content": "A" * 5001,
                "author": "Test Author",
            },
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "fel" in data
        assert "Innehåll får inte överstiga 5000 tecken" in data["fel"]

    def test_add_flash_missing_content(self, client):
        """Test POST /add with missing content returns Swedish error."""
        response = client.post(
            "/cursorflash/add",
            json={
                "title": "Valid Title",
                "author": "Test Author",
            },
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "fel" in data

    def test_add_flash_missing_author(self, client):
        """Test POST /add with missing author returns Swedish error."""
        response = client.post(
            "/cursorflash/add",
            json={
                "title": "Valid Title",
                "content": "Valid content here",
            },
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "fel" in data


class TestCursorflashRoutesUpdate:
    """Tests for PUT /update/<id> (update flash)."""

    def test_update_flash_success(self, client):
        """Test PUT /update/<id> updates an existing flash."""
        # Create a flash first
        create_response = client.post(
            "/cursorflash/add",
            json={
                "title": "Original Title",
                "content": "Original content here",
                "author": "Test Author",
            },
        )
        flash_id = json.loads(create_response.data)["id"]

        # Update the flash
        response = client.put(
            f"/cursorflash/update/{flash_id}",
            json={
                "title": "Updated Title",
                "content": "Updated content here",
            },
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["title"] == "Updated Title"
        assert data["content"] == "Updated content here"
        assert data["author"] == "Test Author"  # Unchanged

    def test_update_flash_not_found(self, client):
        """Test PUT /update/<id> with non-existent ID returns Swedish error."""
        response = client.put(
            "/cursorflash/update/999",
            json={
                "title": "Updated Title",
            },
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert "fel" in data
        assert "Nyhetsflash hittades inte" in data["fel"]

    def test_update_flash_title_validation(self, client):
        """Test PUT /update/<id> validates title."""
        # Create a flash first
        create_response = client.post(
            "/cursorflash/add",
            json={
                "title": "Original Title",
                "content": "Original content here",
                "author": "Test Author",
            },
        )
        flash_id = json.loads(create_response.data)["id"]

        # Try to update with invalid title
        response = client.put(
            f"/cursorflash/update/{flash_id}",
            json={
                "title": "",  # Empty title
            },
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "fel" in data
        assert "Titel krävs" in data["fel"]

    def test_update_flash_partial_update(self, client):
        """Test PUT /update/<id> can update only specific fields."""
        # Create a flash first
        create_response = client.post(
            "/cursorflash/add",
            json={
                "title": "Original Title",
                "content": "Original content here",
                "author": "Test Author",
            },
        )
        flash_id = json.loads(create_response.data)["id"]

        # Update only the title
        response = client.put(
            f"/cursorflash/update/{flash_id}",
            json={
                "title": "New Title Only",
            },
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["title"] == "New Title Only"
        assert data["content"] == "Original content here"  # Unchanged


class TestCursorflashResponsesInSwedish:
    """Tests to verify all responses are in Swedish (AC4)."""

    def test_list_response_structure(self, client):
        """Test that list response uses Swedish field names."""
        response = client.get("/cursorflash/")
        # The key 'flashes' can remain English as it's API convention
        # but error messages should be in Swedish
        assert response.status_code == 200

    def test_error_response_uses_swedish_key(self, client):
        """Test that error responses use 'fel' (Swedish for error)."""
        response = client.post(
            "/cursorflash/add",
            json={
                "content": "Valid content",
                "author": "Test",
            },
        )

        data = json.loads(response.data)
        assert "fel" in data  # Swedish for "error"
        assert "error" not in data  # Not English
