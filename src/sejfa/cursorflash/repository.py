"""Repository layer for NewsFlash data access."""

from abc import ABC, abstractmethod

from src.sejfa.cursorflash.models import NewsFlash


class NewsFlashRepository(ABC):
    """Abstract base class for NewsFlash repository.

    Defines the interface for data access operations.
    """

    @abstractmethod
    def add(self, flash: NewsFlash) -> NewsFlash:
        """Add a new news flash.

        Args:
            flash: NewsFlash to add.

        Returns:
            NewsFlash: Added flash with ID assigned.
        """
        pass

    @abstractmethod
    def get(self, flash_id: int) -> NewsFlash | None:
        """Get a news flash by ID.

        Args:
            flash_id: ID of the flash to retrieve.

        Returns:
            NewsFlash | None: Flash if found, None otherwise.
        """
        pass

    @abstractmethod
    def list_all(self) -> list[NewsFlash]:
        """List all news flashes.

        Returns:
            list[NewsFlash]: All flashes.
        """
        pass

    @abstractmethod
    def update(self, flash: NewsFlash) -> NewsFlash | None:
        """Update an existing news flash.

        Args:
            flash: NewsFlash with updated values.

        Returns:
            NewsFlash | None: Updated flash, or None if not found.
        """
        pass

    @abstractmethod
    def delete(self, flash_id: int) -> bool:
        """Delete a news flash.

        Args:
            flash_id: ID of the flash to delete.

        Returns:
            bool: True if deleted, False if not found.
        """
        pass


class InMemoryNewsFlashRepository(NewsFlashRepository):
    """In-memory implementation of NewsFlash repository.

    Useful for testing with sqlite:///:memory:.
    """

    def __init__(self):
        """Initialize empty storage."""
        self._storage: dict[int, NewsFlash] = {}
        self._next_id: int = 1

    def add(self, flash: NewsFlash) -> NewsFlash:
        """Add a new news flash.

        Args:
            flash: NewsFlash to add (id will be assigned).

        Returns:
            NewsFlash: Added flash with ID assigned.
        """
        flash_with_id = NewsFlash(
            id=self._next_id,
            title=flash.title,
            content=flash.content,
            created_at=flash.created_at,
            author=flash.author,
            published_at=flash.published_at,
        )
        self._storage[self._next_id] = flash_with_id
        self._next_id += 1
        return flash_with_id

    def get(self, flash_id: int) -> NewsFlash | None:
        """Get a news flash by ID.

        Args:
            flash_id: ID of the flash to retrieve.

        Returns:
            NewsFlash | None: Flash if found, None otherwise.
        """
        return self._storage.get(flash_id)

    def list_all(self) -> list[NewsFlash]:
        """List all news flashes.

        Returns:
            list[NewsFlash]: All flashes.
        """
        return list(self._storage.values())

    def update(self, flash: NewsFlash) -> NewsFlash | None:
        """Update an existing news flash.

        Args:
            flash: NewsFlash with updated values.

        Returns:
            NewsFlash | None: Updated flash, or None if not found.
        """
        if flash.id not in self._storage:
            return None
        self._storage[flash.id] = flash
        return flash

    def delete(self, flash_id: int) -> bool:
        """Delete a news flash.

        Args:
            flash_id: ID of the flash to delete.

        Returns:
            bool: True if deleted, False if not found.
        """
        if flash_id in self._storage:
            del self._storage[flash_id]
            return True
        return False

    def reset(self) -> None:
        """Reset storage (for testing).

        Returns:
            None
        """
        self._storage.clear()
        self._next_id = 1
