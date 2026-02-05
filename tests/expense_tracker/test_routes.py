"""Integration tests for ExpenseTracker Flask routes."""

import re

import pytest
from flask import Flask
from flask_wtf.csrf import CSRFProtect

from src.expense_tracker.business.service import ExpenseService
from src.expense_tracker.data.repository import InMemoryExpenseRepository
from src.expense_tracker.presentation.routes import create_expense_blueprint


@pytest.fixture
def app() -> Flask:
    """Create a test Flask application with expense tracker blueprint."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["SECRET_KEY"] = "test-secret-key-for-testing-only"

    # Initialize CSRF protection
    CSRFProtect(app)

    # Set up DI - create repository and service
    repository = InMemoryExpenseRepository()
    service = ExpenseService(repository)

    # Register blueprint with DI
    blueprint = create_expense_blueprint(service)
    app.register_blueprint(blueprint, url_prefix="/expenses")

    return app


@pytest.fixture
def client(app: Flask):
    """Create a test client."""
    return app.test_client()


def get_csrf_token(client):
    """Extract CSRF token from the index page."""
    response = client.get("/expenses/")
    data = response.data.decode("utf-8")
    # Match input tag with name="csrf_token" and capture value
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', data)
    if match:
        return match.group(1)
    return None


class TestIndexRoute:
    """Test GET /expenses/ route - list all expenses."""

    def test_index_returns_200(self, client) -> None:
        """Index page returns 200 OK."""
        response = client.get("/expenses/")
        assert response.status_code == 200

    def test_index_renders_template(self, client) -> None:
        """Index page renders the correct template with Swedish title."""
        response = client.get("/expenses/")
        # Check for Swedish UI text
        assert "Utgifter" in response.data.decode("utf-8")

    def test_index_shows_empty_message(self, client) -> None:
        """Index page shows message when no expenses exist."""
        response = client.get("/expenses/")
        # Should indicate no expenses yet (Swedish)
        assert (
            "Inga utgifter" in response.data.decode("utf-8")
            or "inga" in response.data.decode("utf-8").lower()
        )


class TestAddRoute:
    """Test POST /add route - add new expense."""

    def test_add_valid_expense_redirects(self, client) -> None:
        """Adding valid expense redirects to index."""
        csrf_token = get_csrf_token(client)
        response = client.post(
            "/expenses/add",
            data={
                "title": "Lunch",
                "amount": "50.0",
                "category": "Mat",
                "csrf_token": csrf_token,
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/expenses/" in response.headers["Location"]

    def test_add_valid_expense_shows_in_list(self, client) -> None:
        """Adding valid expense shows it in the list."""
        csrf_token = get_csrf_token(client)
        client.post(
            "/expenses/add",
            data={
                "title": "Lunch",
                "amount": "50.0",
                "category": "Mat",
                "csrf_token": csrf_token,
            },
        )
        response = client.get("/expenses/")
        data = response.data.decode("utf-8")
        assert "Lunch" in data
        assert "50" in data
        assert "Mat" in data

    def test_add_invalid_amount_shows_error(self, client) -> None:
        """Adding expense with invalid amount shows error."""
        csrf_token = get_csrf_token(client)
        response = client.post(
            "/expenses/add",
            data={
                "title": "Test",
                "amount": "-10",
                "category": "Mat",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )
        data = response.data.decode("utf-8")
        # Should show error (Swedish)
        assert (
            "större än 0" in data
            or "greater than 0" in data.lower()
            or "must be greater than" in data.lower()
            or "at least" in data.lower()
        )

    def test_add_empty_title_shows_error(self, client) -> None:
        """Adding expense with empty title shows error."""
        csrf_token = get_csrf_token(client)
        response = client.post(
            "/expenses/add",
            data={
                "title": "",
                "amount": "100",
                "category": "Mat",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )
        data = response.data.decode("utf-8")
        # Should show error about empty title (Swedish) or required
        assert "tom" in data.lower() or "empty" in data.lower() or "required" in data.lower() or "fältet" in data.lower()

    def test_add_invalid_category_shows_error(self, client) -> None:
        """Adding expense with invalid category shows error."""
        csrf_token = get_csrf_token(client)
        response = client.post(
            "/expenses/add",
            data={
                "title": "Test",
                "amount": "100",
                "category": "InvalidCat",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )
        data = response.data.decode("utf-8")
        # Should show error about invalid category (Swedish) or selection
        assert "kategori" in data.lower() or "category" in data.lower() or "valid choice" in data.lower()


class TestSummaryRoute:
    """Test GET /expenses/summary route - show total amount."""

    def test_summary_returns_200(self, client) -> None:
        """Summary page returns 200 OK."""
        response = client.get("/expenses/summary")
        assert response.status_code == 200

    def test_summary_shows_zero_when_empty(self, client) -> None:
        """Summary shows 0 when no expenses."""
        response = client.get("/expenses/summary")
        data = response.data.decode("utf-8")
        # Should show 0 or 0.00
        assert "0" in data

    def test_summary_shows_total_amount(self, client) -> None:
        """Summary shows correct total of all expenses."""
        # Add some expenses
        csrf_token = get_csrf_token(client)
        client.post(
            "/expenses/add",
            data={
                "title": "A",
                "amount": "100",
                "category": "Mat",
                "csrf_token": csrf_token,
            },
        )
        client.post(
            "/expenses/add",
            data={
                "title": "B",
                "amount": "50",
                "category": "Transport",
                "csrf_token": csrf_token,
            },
        )
        client.post(
            "/expenses/add",
            data={
                "title": "C",
                "amount": "25",
                "category": "Boende",
                "csrf_token": csrf_token,
            },
        )

        response = client.get("/expenses/summary")
        data = response.data.decode("utf-8")
        # Total should be 175
        assert "175" in data

    def test_summary_has_swedish_title(self, client) -> None:
        """Summary page has Swedish title."""
        response = client.get("/expenses/summary")
        data = response.data.decode("utf-8")
        # Should have Swedish text for "summary" or "total"
        assert "Sammanfattning" in data or "Totalt" in data
