"""Unit tests for NewsFlashService business logic."""

import pytest

from newsflash_app.business.service import NewsFlashService
from newsflash_app.data.repository import InMemoryNewsFlashRepository


class TestNewsFlashService:
    """Test suite for NewsFlashService."""

    def test_create_flash_with_valid_headline(self):
        """Test creating a flash with headline > 5 chars."""
        repo = InMemoryNewsFlashRepository()
        service = NewsFlashService(repo)

        flash = service.create_flash("Breaking News!", "Summary here", "BREAKING")

        assert flash.headline == "Breaking News!"
        assert flash.summary == "Summary here"
        assert flash.category == "BREAKING"
        assert flash.id > 0

    def test_create_flash_fails_with_short_headline(self):
        """Test that headline <= 5 chars raises ValueError."""
        repo = InMemoryNewsFlashRepository()
        service = NewsFlashService(repo)

        with pytest.raises(ValueError, match="Rubrik måste vara längre än 5 tecken"):
            service.create_flash("Short", "Summary", "TECH")

    def test_create_flash_fails_with_empty_headline(self):
        """Test that empty headline raises ValueError."""
        repo = InMemoryNewsFlashRepository()
        service = NewsFlashService(repo)

        with pytest.raises(ValueError, match="Rubrik måste vara längre än 5 tecken"):
            service.create_flash("", "Summary", "FINANCE")

    def test_create_flash_succeeds_with_6_char_headline(self):
        """Test that headline with exactly 6 chars passes."""
        repo = InMemoryNewsFlashRepository()
        service = NewsFlashService(repo)

        flash = service.create_flash("SPORTS", "Summary", "SPORTS")
        assert flash.headline == "SPORTS"

    def test_create_flash_fails_with_invalid_category(self):
        """Test that invalid category raises ValueError."""
        repo = InMemoryNewsFlashRepository()
        service = NewsFlashService(repo)

        with pytest.raises(
            ValueError, match="Kategori måste vara en av: BREAKING, FINANCE, SPORTS, TECH"
        ):
            service.create_flash("Headline Here", "Summary", "INVALID")

    def test_create_flash_with_all_valid_categories(self):
        """Test all four valid categories work."""
        repo = InMemoryNewsFlashRepository()
        service = NewsFlashService(repo)

        for category in ["BREAKING", "TECH", "FINANCE", "SPORTS"]:
            flash = service.create_flash("Valid Headline", f"Summary for {category}", category)
            assert flash.category == category

    def test_create_multiple_flashes(self):
        """Test creating multiple flash items."""
        repo = InMemoryNewsFlashRepository()
        service = NewsFlashService(repo)

        service.create_flash("First Flash", "Summary 1", "BREAKING")
        service.create_flash("Second Flash", "Summary 2", "TECH")

        flashes = service.get_all_flashes()
        assert len(flashes) == 2

    def test_max_items_per_page_limit(self):
        """Test that max 20 items can be added."""
        repo = InMemoryNewsFlashRepository()
        service = NewsFlashService(repo)

        # Add 20 items
        for i in range(20):
            service.create_flash(f"Headline {i}", f"Summary {i}", "TECH")

        # 21st item should fail
        with pytest.raises(ValueError, match="Kan inte lägga till fler än 20 nyheter per sida"):
            service.create_flash("Too Many", "Summary", "SPORTS")

    def test_get_all_flashes_returns_all_items(self):
        """Test get_all_flashes retrieves all items."""
        repo = InMemoryNewsFlashRepository()
        service = NewsFlashService(repo)

        service.create_flash("Flash One", "Summary 1", "BREAKING")
        service.create_flash("Flash Two", "Summary 2", "FINANCE")

        flashes = service.get_all_flashes()
        assert len(flashes) == 2
        assert flashes[0].headline == "Flash One"
        assert flashes[1].headline == "Flash Two"

    def test_delete_flash_removes_item(self):
        """Test deleting a flash item."""
        repo = InMemoryNewsFlashRepository()
        service = NewsFlashService(repo)

        flash = service.create_flash("To Delete", "Summary", "TECH")
        item_id = flash.id

        service.delete_flash(item_id)

        flashes = service.get_all_flashes()
        assert len(flashes) == 0

    def test_delete_nonexistent_flash_does_nothing(self):
        """Test deleting non-existent item doesn't crash."""
        repo = InMemoryNewsFlashRepository()
        service = NewsFlashService(repo)

        service.delete_flash(999)  # Should not raise error
        assert len(service.get_all_flashes()) == 0

    def test_get_all_flashes_empty_repository(self):
        """Test get_all_flashes on empty repository."""
        repo = InMemoryNewsFlashRepository()
        service = NewsFlashService(repo)

        flashes = service.get_all_flashes()
        assert flashes == []
