"""Repository interfaces and implementations for ExpenseTracker."""

import sqlite3
from abc import ABC, abstractmethod
from decimal import Decimal

from src.expense_tracker.data.models import Expense


class ExpenseRepository(ABC):
    """Abstract repository interface for expense storage."""

    @abstractmethod
    def add(self, expense: Expense) -> Expense:
        """Add an expense to storage.

        Args:
            expense: The expense to add.

        Returns:
            The added expense with assigned ID.
        """
        ...

    @abstractmethod
    def get_all(self) -> list[Expense]:
        """Get all stored expenses.

        Returns:
            List of all expenses.
        """
        ...

    @abstractmethod
    def get_next_id(self) -> int:
        """Get the next available ID.

        Returns:
            The next unique ID.
        """
        ...


class InMemoryExpenseRepository(ExpenseRepository):
    """In-memory SQLite implementation of ExpenseRepository."""

    def __init__(self) -> None:
        """Initialize in-memory SQLite database."""
        self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._create_table()

    def _create_table(self) -> None:
        """Create the expenses table."""
        cursor = self._conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount TEXT NOT NULL,
                category TEXT NOT NULL
            )
        """)
        self._conn.commit()

    def add(self, expense: Expense) -> Expense:
        """Add an expense to storage.

        Args:
            expense: The expense to add.

        Returns:
            The added expense with assigned ID.
        """
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (title, amount, category) VALUES (?, ?, ?)",
            (expense.title, str(expense.amount), expense.category),
        )
        self._conn.commit()

        return Expense(
            id=cursor.lastrowid,
            title=expense.title,
            amount=expense.amount,
            category=expense.category,
        )

    def get_all(self) -> list[Expense]:
        """Get all stored expenses.

        Returns:
            List of all expenses.
        """
        cursor = self._conn.cursor()
        cursor.execute("SELECT id, title, amount, category FROM expenses")
        rows = cursor.fetchall()
        return [
            Expense(id=row[0], title=row[1], amount=Decimal(row[2]), category=row[3])
            for row in rows
        ]

    def get_next_id(self) -> int:
        """Get the next available ID.

        Returns:
            The next unique ID.
        """
        cursor = self._conn.cursor()
        cursor.execute("SELECT MAX(id) FROM expenses")
        row = cursor.fetchone()
        max_id = row[0] if row[0] is not None else 0
        return max_id + 1
