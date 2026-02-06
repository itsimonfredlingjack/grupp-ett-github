"""Tests for News Flash newsletter app."""

from app import create_app


class TestNewsFlashIndex:
    """Tests for the News Flash index page."""

    def test_index_returns_200(self):
        """GET / should return HTTP 200."""
        app = create_app()
        client = app.test_client()
        response = client.get("/")
        assert response.status_code == 200

    def test_index_contains_news_flash(self):
        """Index page should contain 'News Flash' text."""
        app = create_app()
        client = app.test_client()
        response = client.get("/")
        assert b"News Flash" in response.data


class TestNewsFlashSubscribe:
    """Tests for the subscription form page."""

    def test_subscribe_returns_200(self):
        """GET /subscribe should return HTTP 200."""
        app = create_app()
        client = app.test_client()
        response = client.get("/subscribe")
        assert response.status_code == 200

    def test_subscribe_contains_form(self):
        """Subscribe page should contain a form."""
        app = create_app()
        client = app.test_client()
        response = client.get("/subscribe")
        assert b"<form" in response.data
        assert b"email" in response.data.lower()


class TestNewsFlashSubscribeConfirm:
    """Tests for the subscription confirmation."""

    def test_subscribe_confirm_returns_200(self):
        """POST /subscribe/confirm with valid data should return HTTP 200."""
        app = create_app()
        client = app.test_client()
        response = client.post(
            "/subscribe/confirm",
            data={"email": "test@example.com", "name": "Test User"},
        )
        assert response.status_code == 200

    def test_subscribe_confirm_shows_email(self):
        """Thank you page should display the submitted email."""
        app = create_app()
        client = app.test_client()
        response = client.post(
            "/subscribe/confirm",
            data={"email": "test@example.com", "name": "Test User"},
        )
        assert b"test@example.com" in response.data

    def test_subscribe_confirm_shows_name(self):
        """Thank you page should display the submitted name."""
        app = create_app()
        client = app.test_client()
        response = client.post(
            "/subscribe/confirm",
            data={"email": "test@example.com", "name": "Test User"},
        )
        assert b"Test User" in response.data
