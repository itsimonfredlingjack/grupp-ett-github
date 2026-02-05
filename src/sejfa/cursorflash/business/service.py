"""Business logic for Cursorflash.

This module contains the FlashService which handles all business rules
and validation. It has NO Flask dependencies - pure Python only.
"""

from __future__ import annotations

from src.sejfa.cursorflash.data.models import Flash
from src.sejfa.cursorflash.data.repository import FlashRepository


class ValidationError(Exception):
    """Raised when validation fails."""

    pass


class FlashService:
    """Service for managing news flashes with business rules.

    This service enforces:
    - Content must be non-empty and max 280 chars
    - Severity must be between 1 and 5
    """

    def __init__(self, repository: FlashRepository) -> None:
        """Initialize service with repository.

        Args:
            repository: Flash repository for storage
        """
        self._repository = repository

    def create_flash(self, content: str, severity: int) -> Flash:
        """Create a new flash with validation.

        Args:
            content: Flash message content
            severity: Severity level (1-5)

        Returns:
            Created flash with assigned ID

        Raises:
            ValidationError: If validation fails
        """
        # Validate content length
        if not content or len(content.strip()) == 0:
            raise ValidationError("Innehållet får inte vara tomt")

        if len(content) > 280:
            raise ValidationError("Innehållet får max vara 280 tecken")

        # Validate severity range
        if severity < 1 or severity > 5:
            raise ValidationError("Allvarlighetsgrad måste vara mellan 1 och 5")

        # Create and store flash
        flash = Flash(id=0, content=content, severity=severity)
        return self._repository.add(flash)

    def get_all_flashes(self) -> list[Flash]:
        """Get all flashes.

        Returns:
            List of all flashes
        """
        return self._repository.get_all()

    def clear_flashes(self) -> None:
        """Clear all flashes."""
        self._repository.clear()
