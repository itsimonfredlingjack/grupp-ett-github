"""Unit tests for the NewsService."""

import pytest

from cursor_newsletter_app.models import NewsItem
from cursor_newsletter_app.repository import InMemoryRepository
from cursor_newsletter_app.service import NewsService


@pytest.fixture
def repository() -> InMemoryRepository:
    """Create a fresh in-memory repository for each test."""
    return InMemoryRepository()


@pytest.fixture
def service(repository: InMemoryRepository) -> NewsService:
    """Create a service with the in-memory repository."""
    return NewsService(repository)


class TestNewsService:
    """Tests for NewsService business logic."""

    def test_create_news_with_valid_title(self, service: NewsService) -> None:
        """Test creating a news item with a valid title."""
        item = service.create_news("Breaking News", "Important story content")

        assert item.title == "Breaking News"
        assert item.content == "Important story content"
        assert item.id > 0

    def test_create_news_fails_with_short_title(self, service: NewsService) -> None:
        """Test that creating news with title <= 3 chars raises ValueError."""
        with pytest.raises(ValueError, match="Titel måste vara längre än 3 tecken"):
            service.create_news("ABC", "Content")

    def test_create_news_fails_with_empty_title(self, service: NewsService) -> None:
        """Test that creating news with empty title raises ValueError."""
        with pytest.raises(ValueError, match="Titel måste vara längre än 3 tecken"):
            service.create_news("", "Content")

    def test_create_news_succeeds_with_4_char_title(self, service: NewsService) -> None:
        """Test that a 4-character title is valid."""
        item = service.create_news("ABCD", "Content")
        assert item.title == "ABCD"

    def test_create_multiple_news_items(self, service: NewsService) -> None:
        """Test creating multiple news items."""
        item1 = service.create_news("First News", "Content 1")
        item2 = service.create_news("Second News", "Content 2")

        assert item1.id != item2.id
        assert len(service.get_news()) == 2

    def test_max_items_per_page_limit(self, service: NewsService) -> None:
        """Test that max 10 items can be created."""
        # Create 10 items
        for i in range(10):
            service.create_news(f"News Item {i + 1}", f"Content {i + 1}")

        # 11th item should fail
        with pytest.raises(ValueError, match="Max 10 nyhetsartiklar är tillåtet"):
            service.create_news("News Item 11", "Content 11")

    def test_get_news_returns_all_items(self, service: NewsService) -> None:
        """Test that get_news returns all created items."""
        service.create_news("News 1", "Content 1")
        service.create_news("News 2", "Content 2")
        service.create_news("News 3", "Content 3")

        items = service.get_news()
        assert len(items) == 3
        assert all(isinstance(item, NewsItem) for item in items)

    def test_delete_news_removes_item(self, service: NewsService) -> None:
        """Test deleting a news item."""
        item = service.create_news("To Delete", "Content")
        service.delete_news(item.id)

        items = service.get_news()
        assert len(items) == 0

    def test_delete_nonexistent_news_does_nothing(self, service: NewsService) -> None:
        """Test that deleting a nonexistent item doesn't raise an error."""
        service.delete_news(999)  # Should not raise
        assert len(service.get_news()) == 0

    def test_get_news_empty_repository(self, service: NewsService) -> None:
        """Test that get_news returns empty list for empty repository."""
        items = service.get_news()
        assert items == []
