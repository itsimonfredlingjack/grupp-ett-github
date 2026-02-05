"""Repository for Flash storage."""

from __future__ import annotations

from typing import Protocol

from src.sejfa.cursorflash.data.models import Flash


class FlashRepository(Protocol):
    """Abstract interface for Flash storage."""

    def add(self, flash: Flash) -> Flash:
        """Add a flash and return it with assigned ID.

        Args:
            flash: Flash to add

        Returns:
            Flash with assigned ID
        """
        ...  # pragma: no cover

    def get_all(self) -> list[Flash]:
        """Get all flashes.

        Returns:
            List of all flashes
        """
        ...  # pragma: no cover

    def clear(self) -> None:
        """Clear all flashes."""
        ...  # pragma: no cover


class InMemoryFlashRepository:
    """In-memory implementation of FlashRepository."""

    def __init__(self) -> None:
        """Initialize empty repository."""
        self._flashes: list[Flash] = []
        self._next_id: int = 1

    def add(self, flash: Flash) -> Flash:
        """Add a flash and return it with assigned ID.

        Args:
            flash: Flash to add

        Returns:
            Flash with assigned ID
        """
        new_flash = Flash(
            id=self._next_id, content=flash.content, severity=flash.severity
        )
        self._flashes.append(new_flash)
        self._next_id += 1
        return new_flash

    def get_all(self) -> list[Flash]:
        """Get all flashes.

        Returns:
            List of all flashes
        """
        return self._flashes.copy()

    def clear(self) -> None:
        """Clear all flashes."""
        self._flashes.clear()
        self._next_id = 1
