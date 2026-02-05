"""Integration tests for News Flash Flask application."""

import pytest

from newsflash_app.flask_app import create_app


class TestFlaskApp:
    """Integration test suite for Flask routes."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app({"TESTING": True})
        return app.test_client()

    def test_index_page_loads(self, client):
        """Test that index page returns 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_index_shows_empty_state_initially(self, client):
        """Test that index shows empty state when no flashes exist."""
        response = client.get("/")
        assert b"Inga nyheter" in response.data

    def test_add_flash_with_valid_data(self, client):
        """Test adding a flash with valid data."""
        response = client.post(
            "/add",
            data={
                "headline": "Breaking News Today",
                "summary": "This is a test summary",
                "category": "BREAKING",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302  # Redirect

    def test_add_flash_with_short_headline(self, client):
        """Test adding flash with short headline returns 400."""
        response = client.post(
            "/add",
            data={"headline": "Short", "summary": "Test", "category": "TECH"},
            follow_redirects=False,
        )
        assert response.status_code == 400
        assert "Rubrik måste vara längre än 5 tecken" in response.data.decode()

    def test_add_flash_redirects_to_index(self, client):
        """Test that successful add redirects to index."""
        response = client.post(
            "/add",
            data={
                "headline": "Valid Headline",
                "summary": "Summary text",
                "category": "FINANCE",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Valid Headline" in response.data

    def test_multiple_flashes_display(self, client):
        """Test that multiple flashes are displayed."""
        client.post(
            "/add",
            data={
                "headline": "First Flash",
                "summary": "First summary",
                "category": "TECH",
            },
        )
        client.post(
            "/add",
            data={
                "headline": "Second Flash",
                "summary": "Second summary",
                "category": "SPORTS",
            },
        )

        response = client.get("/")
        assert b"First Flash" in response.data
        assert b"Second Flash" in response.data

    def test_delete_flash_item(self, client):
        """Test deleting a flash item."""
        # Add flash
        client.post(
            "/add",
            data={
                "headline": "To Be Deleted",
                "summary": "This will be deleted",
                "category": "BREAKING",
            },
        )

        # Verify it exists
        response = client.get("/")
        assert b"To Be Deleted" in response.data

        # Delete it (ID should be 1 for first item)
        response = client.get("/delete/1", follow_redirects=True)
        assert response.status_code == 200
        assert b"To Be Deleted" not in response.data

    def test_max_items_limit_error(self, client):
        """Test that adding more than 20 items returns error."""
        # Add 20 items
        for i in range(20):
            client.post(
                "/add",
                data={
                    "headline": f"Headline Number {i}",
                    "summary": f"Summary {i}",
                    "category": "TECH",
                },
            )

        # Try to add 21st
        response = client.post(
            "/add",
            data={
                "headline": "Too Many Items",
                "summary": "This should fail",
                "category": "SPORTS",
            },
        )
        assert response.status_code == 400
        assert "Kan inte lägga till fler än 20 nyheter per sida" in response.data.decode()

    def test_form_submission_preserves_state(self, client):
        """Test that form submission works and state persists."""
        client.post(
            "/add",
            data={
                "headline": "Persistent Flash",
                "summary": "Should persist",
                "category": "FINANCE",
            },
        )

        # Reload page
        response = client.get("/")
        assert b"Persistent Flash" in response.data
        assert b"Should persist" in response.data

    def test_delete_nonexistent_item_doesnt_crash(self, client):
        """Test that deleting non-existent item doesn't crash."""
        response = client.get("/delete/999", follow_redirects=True)
        assert response.status_code == 200

    def test_invalid_category_returns_error(self, client):
        """Test that invalid category returns error."""
        response = client.post(
            "/add",
            data={
                "headline": "Valid Headline",
                "summary": "Summary",
                "category": "INVALID",
            },
        )
        assert response.status_code == 400
        assert "Kategori måste vara en av" in response.data.decode()

    def test_all_categories_display_correctly(self, client):
        """Test that all four categories display correctly."""
        categories = ["BREAKING", "TECH", "FINANCE", "SPORTS"]

        for cat in categories:
            client.post(
                "/add",
                data={
                    "headline": f"{cat} Headline",
                    "summary": f"Summary for {cat}",
                    "category": cat,
                },
            )

        response = client.get("/")
        for cat in categories:
            assert cat.encode() in response.data
