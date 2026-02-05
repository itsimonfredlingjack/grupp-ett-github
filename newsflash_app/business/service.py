"""Business logic service for news flash management."""

from newsflash_app.data.models import NewsFlash
from newsflash_app.data.repository import NewsFlashRepository


MAX_ITEMS_PER_PAGE = 20


class NewsFlashService:
    """Service for managing news flash items."""

    def __init__(self, repository: NewsFlashRepository) -> None:
        """Initialize with repository dependency.

        Args:
            repository: Repository implementation for persistence.
        """
        self._repository = repository

    def create_flash(self, headline: str, summary: str, category: str) -> NewsFlash:
        """Create a new news flash item.

        Args:
            headline: The headline text (must be > 5 chars).
            summary: The summary text.
            category: Must be one of BREAKING, TECH, FINANCE, SPORTS.

        Returns:
            The created NewsFlash instance.

        Raises:
            ValueError: If headline is too short or category is invalid.
            ValueError: If max items limit would be exceeded.
        """
        current_count = len(self._repository.get_all())
        if current_count >= MAX_ITEMS_PER_PAGE:
            raise ValueError(
                f"Kan inte lägga till fler än {MAX_ITEMS_PER_PAGE} nyheter per sida"
            )

        item = NewsFlash(id=0, headline=headline, summary=summary, category=category)
        self._repository.add(item)
        return item

    def get_all_flashes(self) -> list[NewsFlash]:
        """Retrieve all news flash items.

        Returns:
            List of all NewsFlash items.
        """
        return self._repository.get_all()

    def delete_flash(self, item_id: int) -> None:
        """Delete a news flash item.

        Args:
            item_id: The ID of the item to delete.
        """
        self._repository.delete(item_id)
