"""Unit tests for ExpenseService business logic."""

from decimal import Decimal

import pytest

from src.expense_tracker.business.exceptions import (
    InvalidAmountError,
    InvalidCategoryError,
    InvalidTitleError,
)
from src.expense_tracker.business.service import ExpenseService
from src.expense_tracker.data.repository import InMemoryExpenseRepository


class TestExpenseServiceValidation:
    """Test business rules for expense validation."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.repository = InMemoryExpenseRepository()
        self.service = ExpenseService(self.repository)

    def test_amount_must_be_greater_than_zero(self) -> None:
        """Amount must be > 0 - cannot log negative expenses."""
        with pytest.raises(InvalidAmountError) as exc_info:
            self.service.add_expense(
                title="Test", amount=Decimal("-10.0"), category="Mat"
            )
        assert "greater than 0" in str(exc_info.value).lower()

    def test_amount_zero_is_invalid(self) -> None:
        """Amount of exactly 0 is also invalid."""
        with pytest.raises(InvalidAmountError):
            self.service.add_expense(title="Test", amount=Decimal("0.0"), category="Mat")

    def test_amount_positive_is_valid(self) -> None:
        """Positive amount should be accepted."""
        expense = self.service.add_expense(
            title="Lunch", amount=Decimal("50.0"), category="Mat"
        )
        assert expense.amount == Decimal("50.0")

    def test_title_cannot_be_empty(self) -> None:
        """Title must not be empty."""
        with pytest.raises(InvalidTitleError) as exc_info:
            self.service.add_expense(title="", amount=Decimal("100.0"), category="Mat")
        error_msg = str(exc_info.value).lower()
        assert "empty" in error_msg or "tom" in error_msg

    def test_title_cannot_be_whitespace_only(self) -> None:
        """Title with only whitespace is considered empty."""
        with pytest.raises(InvalidTitleError):
            self.service.add_expense(title="   ", amount=Decimal("100.0"), category="Mat")

    def test_title_valid(self) -> None:
        """Valid title should be accepted."""
        expense = self.service.add_expense(
            title="Groceries", amount=Decimal("200.0"), category="Mat"
        )
        assert expense.title == "Groceries"

    def test_category_must_be_valid(self) -> None:
        """Category must be one of: Mat, Transport, Boende, Övrigt."""
        with pytest.raises(InvalidCategoryError) as exc_info:
            self.service.add_expense(
                title="Test", amount=Decimal("100.0"), category="Invalid"
            )
        error_msg = str(exc_info.value).lower()
        assert "kategori" in error_msg or "category" in error_msg

    def test_category_mat_is_valid(self) -> None:
        """Mat is a valid category."""
        expense = self.service.add_expense(
            title="Lunch", amount=Decimal("50.0"), category="Mat"
        )
        assert expense.category == "Mat"

    def test_category_transport_is_valid(self) -> None:
        """Transport is a valid category."""
        expense = self.service.add_expense(
            title="Bus", amount=Decimal("30.0"), category="Transport"
        )
        assert expense.category == "Transport"

    def test_category_boende_is_valid(self) -> None:
        """Boende is a valid category."""
        expense = self.service.add_expense(
            title="Rent", amount=Decimal("8000.0"), category="Boende"
        )
        assert expense.category == "Boende"

    def test_category_ovrigt_is_valid(self) -> None:
        """Övrigt is a valid category."""
        expense = self.service.add_expense(
            title="Other", amount=Decimal("100.0"), category="Övrigt"
        )
        assert expense.category == "Övrigt"


class TestExpenseServiceOperations:
    """Test CRUD operations on expenses."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.repository = InMemoryExpenseRepository()
        self.service = ExpenseService(self.repository)

    def test_add_expense_assigns_id(self) -> None:
        """Adding an expense should assign an ID."""
        expense = self.service.add_expense(
            title="Test", amount=Decimal("100.0"), category="Mat"
        )
        assert expense.id is not None
        assert expense.id > 0

    def test_get_all_expenses_empty(self) -> None:
        """Getting all expenses when empty returns empty list."""
        expenses = self.service.get_all_expenses()
        assert expenses == []

    def test_get_all_expenses_returns_added(self) -> None:
        """Getting all expenses returns previously added expenses."""
        self.service.add_expense(title="Lunch", amount=Decimal("50.0"), category="Mat")
        self.service.add_expense(
            title="Bus", amount=Decimal("30.0"), category="Transport"
        )
        expenses = self.service.get_all_expenses()
        assert len(expenses) == 2

    def test_get_total_amount_empty(self) -> None:
        """Total amount with no expenses is 0."""
        total = self.service.get_total_amount()
        assert total == Decimal("0.00")

    def test_get_total_amount_sums_all(self) -> None:
        """Total amount sums all expense amounts."""
        self.service.add_expense(title="Lunch", amount=Decimal("50.0"), category="Mat")
        self.service.add_expense(
            title="Bus", amount=Decimal("30.0"), category="Transport"
        )
        self.service.add_expense(
            title="Rent", amount=Decimal("100.0"), category="Boende"
        )
        total = self.service.get_total_amount()
        assert total == Decimal("180.0")
