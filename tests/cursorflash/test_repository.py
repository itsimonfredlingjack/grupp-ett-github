"""Tests for NewsFlash repository layer."""

from datetime import datetime

from src.sejfa.cursorflash.models import NewsFlash
from src.sejfa.cursorflash.repository import InMemoryNewsFlashRepository


class TestInMemoryNewsFlashRepository:
    """Tests for InMemoryNewsFlashRepository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repo = InMemoryNewsFlashRepository()

    def test_add_assigns_id(self):
        """Test that add assigns an ID to the flash."""
        flash = NewsFlash(
            id=0,
            title="Test",
            content="Test content",
            created_at=datetime.now(),
            author="Author",
        )
        result = self.repo.add(flash)
        assert result.id == 1

    def test_add_increments_id(self):
        """Test that add increments ID for each flash."""
        flash1 = NewsFlash(
            id=0,
            title="Test 1",
            content="Test content",
            created_at=datetime.now(),
            author="Author",
        )
        flash2 = NewsFlash(
            id=0,
            title="Test 2",
            content="Test content",
            created_at=datetime.now(),
            author="Author",
        )
        result1 = self.repo.add(flash1)
        result2 = self.repo.add(flash2)
        assert result1.id == 1
        assert result2.id == 2

    def test_get_returns_flash(self):
        """Test that get returns the correct flash."""
        flash = NewsFlash(
            id=0,
            title="Test",
            content="Test content",
            created_at=datetime.now(),
            author="Author",
        )
        added = self.repo.add(flash)
        result = self.repo.get(added.id)
        assert result is not None
        assert result.title == "Test"

    def test_get_returns_none_for_missing(self):
        """Test that get returns None for missing ID."""
        result = self.repo.get(999)
        assert result is None

    def test_list_all_returns_all(self):
        """Test that list_all returns all flashes."""
        flash1 = NewsFlash(
            id=0,
            title="Test 1",
            content="Content 1",
            created_at=datetime.now(),
            author="Author",
        )
        flash2 = NewsFlash(
            id=0,
            title="Test 2",
            content="Content 2",
            created_at=datetime.now(),
            author="Author",
        )
        self.repo.add(flash1)
        self.repo.add(flash2)
        result = self.repo.list_all()
        assert len(result) == 2

    def test_update_existing_flash(self):
        """Test that update modifies an existing flash."""
        flash = NewsFlash(
            id=0,
            title="Original",
            content="Original content",
            created_at=datetime.now(),
            author="Author",
        )
        added = self.repo.add(flash)
        updated_flash = NewsFlash(
            id=added.id,
            title="Updated",
            content="Updated content",
            created_at=added.created_at,
            author=added.author,
        )
        result = self.repo.update(updated_flash)
        assert result is not None
        assert result.title == "Updated"

    def test_update_returns_none_for_missing(self):
        """Test that update returns None for missing ID."""
        flash = NewsFlash(
            id=999,
            title="Test",
            content="Test content",
            created_at=datetime.now(),
            author="Author",
        )
        result = self.repo.update(flash)
        assert result is None

    def test_delete_existing_flash(self):
        """Test that delete removes an existing flash."""
        flash = NewsFlash(
            id=0,
            title="Test",
            content="Test content",
            created_at=datetime.now(),
            author="Author",
        )
        added = self.repo.add(flash)
        result = self.repo.delete(added.id)
        assert result is True
        assert self.repo.get(added.id) is None

    def test_delete_returns_false_for_missing(self):
        """Test that delete returns False for missing ID."""
        result = self.repo.delete(999)
        assert result is False

    def test_reset_clears_storage(self):
        """Test that reset clears all storage."""
        flash = NewsFlash(
            id=0,
            title="Test",
            content="Test content",
            created_at=datetime.now(),
            author="Author",
        )
        self.repo.add(flash)
        self.repo.reset()
        assert self.repo.list_all() == []

    def test_reset_resets_id_counter(self):
        """Test that reset resets the ID counter."""
        flash = NewsFlash(
            id=0,
            title="Test",
            content="Test content",
            created_at=datetime.now(),
            author="Author",
        )
        self.repo.add(flash)
        self.repo.reset()
        new_flash = self.repo.add(flash)
        assert new_flash.id == 1
