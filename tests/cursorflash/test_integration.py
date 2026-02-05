"""Integration tests for Cursorflash."""

from __future__ import annotations

import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.sejfa.cursorflash.app import create_app


@pytest.fixture
def app() -> Flask:
    """Create test application."""
    return create_app()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create test client."""
    return app.test_client()


class TestCursorflashIntegration:
    """Test complete Cursorflash workflow."""

    def test_index_page_loads(self, client: FlaskClient) -> None:
        """Test that index page loads successfully."""
        response = client.get("/cursorflash/")
        assert response.status_code == 200
        assert b"Hello Gemini Claude Cursor Codex world" in response.data

    def test_index_shows_swedish_text(self, client: FlaskClient) -> None:
        """Test that UI is in Swedish."""
        response = client.get("/cursorflash/")
        assert b"Cursorflash" in response.data
        assert b"Snabba Nyheter" in response.data
        assert response.status_code == 200

    def test_add_flash_success(self, client: FlaskClient) -> None:
        """Test adding a valid flash."""
        response = client.post(
            "/cursorflash/add",
            data={"content": "Test flash", "severity": "3"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Flash tillagd!" in response.data
        assert b"Test flash" in response.data

    def test_add_flash_empty_content_shows_error(self, client: FlaskClient) -> None:
        """Test that empty content shows error message."""
        response = client.post(
            "/cursorflash/add",
            data={"content": "", "severity": "3"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"tomt" in response.data.lower()

    def test_add_flash_invalid_severity_shows_error(self, client: FlaskClient) -> None:
        """Test that invalid severity shows error message."""
        response = client.post(
            "/cursorflash/add",
            data={"content": "Test", "severity": "6"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"1" in response.data and b"5" in response.data

    def test_add_flash_too_long_shows_error(self, client: FlaskClient) -> None:
        """Test that content over 280 chars shows error."""
        long_content = "x" * 281
        response = client.post(
            "/cursorflash/add",
            data={"content": long_content, "severity": "3"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"280" in response.data

    def test_clear_removes_all_flashes(self, client: FlaskClient) -> None:
        """Test that clear route removes all flashes."""
        # Add a flash
        client.post(
            "/cursorflash/add",
            data={"content": "Test", "severity": "2"},
        )

        # Clear
        response = client.get("/cursorflash/clear", follow_redirects=True)
        assert response.status_code == 200
        assert b"rensade" in response.data.lower()

    def test_multiple_flashes_display_correctly(self, client: FlaskClient) -> None:
        """Test that multiple flashes are displayed."""
        client.post(
            "/cursorflash/add",
            data={"content": "First flash", "severity": "1"},
        )
        client.post(
            "/cursorflash/add",
            data={"content": "Second flash", "severity": "5"},
        )

        response = client.get("/cursorflash/")
        assert b"First flash" in response.data
        assert b"Second flash" in response.data

    def test_severity_levels_all_work(self, client: FlaskClient) -> None:
        """Test that all severity levels (1-5) work."""
        for severity in range(1, 6):
            response = client.post(
                "/cursorflash/add",
                data={"content": f"Severity {severity}", "severity": str(severity)},
                follow_redirects=True,
            )
            assert response.status_code == 200
            assert f"Severity {severity}".encode() in response.data


class TestAppFactory:
    """Test app factory configuration."""

    def test_create_app_returns_flask_app(self) -> None:
        """Test that create_app returns a Flask instance."""
        app = create_app()
        assert isinstance(app, Flask)

    def test_app_has_cursorflash_blueprint(self) -> None:
        """Test that app has cursorflash blueprint registered."""
        app = create_app()
        assert "cursorflash" in app.blueprints
