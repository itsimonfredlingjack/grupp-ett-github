"""Business logic layer for NewsFlash."""

from datetime import datetime

from src.sejfa.cursorflash.models import NewsFlash
from src.sejfa.cursorflash.repository import NewsFlashRepository


class ValidationError(Exception):
    """Exception raised when validation fails."""

    pass


class NewsFlashService:
    """Service for managing news flashes.

    Implements business rules and validation.
    Uses dependency injection for repository.

    Attributes:
        repository: NewsFlashRepository instance for data access.
    """

    # Validation constants
    TITLE_MAX_LENGTH = 100
    CONTENT_MIN_LENGTH = 10
    CONTENT_MAX_LENGTH = 5000

    def __init__(self, repository: NewsFlashRepository):
        """Initialize service with repository.

        Args:
            repository: NewsFlashRepository instance.
        """
        self._repository = repository

    def _validate_title(self, title: str) -> None:
        """Validate title against business rules.

        Args:
            title: Title to validate.

        Raises:
            ValidationError: If title is invalid.
        """
        if not title or not title.strip():
            raise ValidationError("Titel krävs")
        if len(title) > self.TITLE_MAX_LENGTH:
            raise ValidationError(
                f"Titel får inte överstiga {self.TITLE_MAX_LENGTH} tecken"
            )

    def _validate_content(self, content: str) -> None:
        """Validate content against business rules.

        Args:
            content: Content to validate.

        Raises:
            ValidationError: If content is invalid.
        """
        if len(content) < self.CONTENT_MIN_LENGTH:
            raise ValidationError(
                f"Innehåll måste vara minst {self.CONTENT_MIN_LENGTH} tecken"
            )
        if len(content) > self.CONTENT_MAX_LENGTH:
            raise ValidationError(
                f"Innehåll får inte överstiga {self.CONTENT_MAX_LENGTH} tecken"
            )

    def create_flash(
        self,
        title: str,
        content: str,
        author: str,
        published_at: datetime | None = None,
    ) -> NewsFlash:
        """Create a new news flash.

        Args:
            title: Title of the flash.
            content: Content of the flash.
            author: Author of the flash.
            published_at: Optional publication datetime.

        Returns:
            NewsFlash: Created flash with ID assigned.

        Raises:
            ValidationError: If validation fails.
        """
        self._validate_title(title)
        self._validate_content(content)

        flash = NewsFlash(
            id=0,  # Will be assigned by repository
            title=title,
            content=content,
            created_at=datetime.now(),
            author=author,
            published_at=published_at,
        )

        return self._repository.add(flash)

    def list_flashes(self) -> list[NewsFlash]:
        """List all news flashes.

        Returns:
            list[NewsFlash]: All flashes.
        """
        return self._repository.list_all()

    def get_flash(self, flash_id: int) -> NewsFlash | None:
        """Get a news flash by ID.

        Args:
            flash_id: ID of the flash.

        Returns:
            NewsFlash | None: Flash if found, None otherwise.
        """
        return self._repository.get(flash_id)

    def update_flash(
        self,
        flash_id: int,
        title: str | None = None,
        content: str | None = None,
        published_at: datetime | None = None,
    ) -> NewsFlash | None:
        """Update an existing news flash.

        Args:
            flash_id: ID of the flash to update.
            title: New title (optional).
            content: New content (optional).
            published_at: New publication datetime (optional).

        Returns:
            NewsFlash | None: Updated flash, or None if not found.

        Raises:
            ValidationError: If validation fails.
        """
        existing = self._repository.get(flash_id)
        if existing is None:
            return None

        # Validate new values if provided
        new_title = title if title is not None else existing.title
        new_content = content if content is not None else existing.content

        self._validate_title(new_title)
        self._validate_content(new_content)

        new_published_at = (
            published_at if published_at is not None else existing.published_at
        )
        updated_flash = NewsFlash(
            id=existing.id,
            title=new_title,
            content=new_content,
            created_at=existing.created_at,
            author=existing.author,
            published_at=new_published_at,
        )

        return self._repository.update(updated_flash)

    def delete_flash(self, flash_id: int) -> bool:
        """Delete a news flash.

        Args:
            flash_id: ID of the flash to delete.

        Returns:
            bool: True if deleted, False if not found.
        """
        return self._repository.delete(flash_id)
