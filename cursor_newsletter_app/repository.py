"""Repository protocol and in-memory implementation."""

from abc import ABC, abstractmethod

from cursor_newsletter_app.models import NewsItem


class NewsRepository(ABC):
    """Abstract base class for news repository."""

    @abstractmethod
    def add(self, item: NewsItem) -> None:
        """Add a news item to the repository."""
        pass

    @abstractmethod
    def get_all(self) -> list[NewsItem]:
        """Get all news items."""
        pass

    @abstractmethod
    def delete(self, item_id: int) -> None:
        """Delete a news item by ID."""
        pass

    @abstractmethod
    def get_by_id(self, item_id: int) -> NewsItem | None:
        """Get a news item by ID."""
        pass


class InMemoryRepository(NewsRepository):
    """In-memory implementation of NewsRepository for testing and MVP."""

    def __init__(self) -> None:
        """Initialize the in-memory repository."""
        self._items: dict[int, NewsItem] = {}
        self._next_id: int = 1

    def add(self, item: NewsItem) -> None:
        """Add a news item to the repository."""
        if item.id == 0:
            item.id = self._next_id
            self._next_id += 1
        self._items[item.id] = item

    def get_all(self) -> list[NewsItem]:
        """Get all news items."""
        return list(self._items.values())

    def delete(self, item_id: int) -> None:
        """Delete a news item by ID."""
        if item_id in self._items:
            del self._items[item_id]

    def get_by_id(self, item_id: int) -> NewsItem | None:
        """Get a news item by ID."""
        return self._items.get(item_id)
