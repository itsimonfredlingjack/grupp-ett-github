"""Business logic service for newsletter management."""

from cursor_newsletter_app.models import NewsItem
from cursor_newsletter_app.repository import NewsRepository


class NewsService:
    """Service for managing news items with business rules."""

    MAX_ITEMS_PER_PAGE = 10

    def __init__(self, repository: NewsRepository) -> None:
        """Initialize the service with a repository.

        Args:
            repository: The repository implementation to use for data access.
        """
        self.repository = repository

    def create_news(self, title: str, content: str) -> NewsItem:
        """Create and add a new news item.

        Args:
            title: The news headline (must be > 3 characters).
            content: The news content.

        Returns:
            The created NewsItem.

        Raises:
            ValueError: If title is too short or too many items exist.
        """
        if len(title) <= 3:
            raise ValueError("Titel måste vara längre än 3 tecken")

        all_items = self.repository.get_all()
        if len(all_items) >= self.MAX_ITEMS_PER_PAGE:
            raise ValueError(
                f"Max {self.MAX_ITEMS_PER_PAGE} nyhetsartiklar är tillåtet"
            )

        item = NewsItem(id=0, title=title, content=content)
        self.repository.add(item)
        return item

    def get_news(self) -> list[NewsItem]:
        """Get all news items.

        Returns:
            A list of all news items.
        """
        return self.repository.get_all()

    def delete_news(self, item_id: int) -> None:
        """Delete a news item by ID.

        Args:
            item_id: The ID of the item to delete.
        """
        self.repository.delete(item_id)
