"""Integration tests for the Flask application."""

import pytest

from cursor_newsletter_app.flask_app import create_app


@pytest.fixture
def app():
    """Create app for testing."""
    app = create_app({"TESTING": True})
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestFlaskApp:
    """Integration tests for Flask application."""

    def test_index_page_loads(self, client):
        """Test that the index page loads successfully."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Nyhetsbrevet Cursor The Mad" in response.data

    def test_index_shows_empty_state_initially(self, client):
        """Test that index shows empty state when no news items exist."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Inga nyheter" in response.data

    def test_add_news_with_valid_data(self, client):
        """Test adding a news item with valid data."""
        response = client.post(
            "/add",
            data={"title": "Test News", "content": "Test content"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Test News" in response.data

    def test_add_news_with_short_title(self, client):
        """Test adding news with title <= 3 characters returns error."""
        response = client.post("/add", data={"title": "ABC", "content": "Content"})
        assert response.status_code == 400
        assert b"Titel m" in response.data  # Part of Swedish error message

    def test_add_news_redirects_to_index(self, client):
        """Test that adding news redirects to index page."""
        response = client.post(
            "/add",
            data={"title": "News", "content": "Content"},
            follow_redirects=False,
        )
        assert response.status_code == 302  # Redirect status code

    def test_multiple_news_items_display(self, client):
        """Test that multiple news items are displayed."""
        client.post("/add", data={"title": "First News", "content": "Content 1"})
        client.post("/add", data={"title": "Second News", "content": "Content 2"})

        response = client.get("/")
        assert b"First News" in response.data
        assert b"Second News" in response.data

    def test_delete_news_item(self, client):
        """Test deleting a news item."""
        # Add a news item
        client.post("/add", data={"title": "To Delete", "content": "Content"})

        # Get index to find ID
        response = client.get("/")
        assert b"To Delete" in response.data

        # Delete the item (ID 1 is first created)
        response = client.get("/delete/1", follow_redirects=True)
        assert response.status_code == 200
        assert b"To Delete" not in response.data

    def test_max_items_limit_error(self, client):
        """Test that adding more than 10 items returns error."""
        # Add 10 items
        for i in range(10):
            client.post(
                "/add",
                data={"title": f"News {i + 1}", "content": f"Content {i + 1}"},
            )

        # 11th item should fail
        response = client.post(
            "/add", data={"title": "News 11", "content": "Content 11"}
        )
        assert response.status_code == 400
        assert b"Max 10" in response.data

    def test_form_submission_preserves_state(self, client):
        """Test that adding one item doesn't affect others."""
        client.post("/add", data={"title": "First News", "content": "Content 1"})
        response = client.get("/")
        assert response.status_code == 200
        assert b"First News" in response.data

        client.post("/add", data={"title": "Second News", "content": "Content 2"})
        response = client.get("/")
        assert b"First News" in response.data
        assert b"Second News" in response.data

    def test_delete_nonexistent_item_doesnt_crash(self, client):
        """Test that deleting a nonexistent item doesn't crash."""
        response = client.get("/delete/999", follow_redirects=True)
        assert response.status_code == 200
