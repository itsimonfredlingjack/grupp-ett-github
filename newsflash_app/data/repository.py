"""Repository protocol and in-memory implementation."""

from abc import ABC, abstractmethod

from newsflash_app.data.models import NewsFlash


class NewsFlashRepository(ABC):
    """Abstract repository for NewsFlash entities."""

    @abstractmethod
    def add(self, item: NewsFlash) -> None:
        """Add a news flash item."""
        pass

    @abstractmethod
    def get_all(self) -> list[NewsFlash]:
        """Retrieve all news flash items."""
        pass

    @abstractmethod
    def delete(self, item_id: int) -> None:
        """Delete a news flash item by ID."""
        pass


class InMemoryNewsFlashRepository(NewsFlashRepository):
    """In-memory implementation of NewsFlashRepository."""

    def __init__(self) -> None:
        """Initialize with empty storage."""
        self._storage: dict[int, NewsFlash] = {}
        self._next_id = 1

    def add(self, item: NewsFlash) -> None:
        """Add a news flash item."""
        if item.id == 0:
            item.id = self._next_id
            self._next_id += 1
        self._storage[item.id] = item

    def get_all(self) -> list[NewsFlash]:
        """Retrieve all news flash items."""
        return list(self._storage.values())

    def delete(self, item_id: int) -> None:
        """Delete a news flash item by ID."""
        if item_id in self._storage:
            del self._storage[item_id]
