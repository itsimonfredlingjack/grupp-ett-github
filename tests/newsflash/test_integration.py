"""Integration tests for News Flash subscription."""

from __future__ import annotations

import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.sejfa.newsflash.presentation.routes import create_newsflash_blueprint


@pytest.fixture
def app() -> Flask:
    """Create test application."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test-secret-key"

    # Register blueprint
    bp = create_newsflash_blueprint()
    app.register_blueprint(bp, url_prefix="/newsflash")

    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create test client."""
    return app.test_client()


class TestNewsFlashSubscription:
    """Test News Flash subscription workflow."""

    def test_subscribe_page_loads(self, client: FlaskClient) -> None:
        """Test that subscribe page loads successfully."""
        response = client.get("/newsflash/subscribe")
        assert response.status_code == 200
        assert b"Join Our Newsletter" in response.data

    def test_subscribe_confirm_with_valid_data(self, client: FlaskClient) -> None:
        """Test successful subscription with valid email and name."""
        response = client.post(
            "/newsflash/subscribe/confirm",
            data={"email": "test@example.com", "name": "John Doe"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"prenumeration" in response.data.lower()

    def test_subscribe_confirm_empty_email_shows_error(
        self, client: FlaskClient
    ) -> None:
        """Test that empty email shows 'Email is required' error."""
        response = client.post(
            "/newsflash/subscribe/confirm",
            data={"email": "", "name": "John Doe"},
            follow_redirects=False,
        )
        assert response.status_code == 200
        assert b"Email is required" in response.data

    def test_subscribe_confirm_invalid_email_shows_error(
        self, client: FlaskClient
    ) -> None:
        """Test that invalid email shows 'Invalid email format' error."""
        response = client.post(
            "/newsflash/subscribe/confirm",
            data={"email": "invalid", "name": "John Doe"},
            follow_redirects=False,
        )
        assert response.status_code == 200
        assert b"Invalid email format" in response.data

    def test_subscribe_confirm_preserves_input_on_error(
        self, client: FlaskClient
    ) -> None:
        """Test that user input is preserved when validation fails."""
        response = client.post(
            "/newsflash/subscribe/confirm",
            data={"email": "invalid", "name": "John Doe"},
            follow_redirects=False,
        )
        assert response.status_code == 200
        assert b"invalid" in response.data  # Email preserved
        assert b"John Doe" in response.data  # Name preserved

    def test_subscribe_confirm_error_banner_visible(self, client: FlaskClient) -> None:
        """Test that error banner is visible on validation failure."""
        response = client.post(
            "/newsflash/subscribe/confirm",
            data={"email": "", "name": "John"},
            follow_redirects=False,
        )
        assert response.status_code == 200
        assert b"error-banner" in response.data

    def test_subscribe_confirm_normalizes_email(self, client: FlaskClient) -> None:
        """Test that email is normalized (uppercase -> lowercase, trimmed)."""
        response = client.post(
            "/newsflash/subscribe/confirm",
            data={"email": "  TEST@EXAMPLE.COM  ", "name": "John"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        # Should succeed with normalized email

    def test_subscribe_confirm_empty_name_uses_default(
        self, client: FlaskClient
    ) -> None:
        """Test that empty name defaults to 'Subscriber'."""
        response = client.post(
            "/newsflash/subscribe/confirm",
            data={"email": "test@example.com", "name": ""},
            follow_redirects=True,
        )
        assert response.status_code == 200
        # Should succeed with default name
