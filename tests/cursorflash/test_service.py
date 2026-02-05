"""Tests for NewsFlash service layer."""

from datetime import datetime

import pytest

from src.sejfa.cursorflash.models import NewsFlash
from src.sejfa.cursorflash.repository import InMemoryNewsFlashRepository
from src.sejfa.cursorflash.service import NewsFlashService, ValidationError


class TestNewsFlashServiceValidation:
    """Tests for NewsFlash validation rules."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repository = InMemoryNewsFlashRepository()
        self.service = NewsFlashService(repository=self.repository)

    def test_title_required(self):
        """Test that title is required (AC2)."""
        with pytest.raises(ValidationError) as exc_info:
            self.service.create_flash(
                title="",
                content="Valid content here",
                author="Test Author",
            )
        assert "Titel krävs" in str(exc_info.value)

    def test_title_max_100_chars(self):
        """Test that title cannot exceed 100 characters (AC2)."""
        long_title = "A" * 101
        with pytest.raises(ValidationError) as exc_info:
            self.service.create_flash(
                title=long_title,
                content="Valid content here",
                author="Test Author",
            )
        assert "Titel får inte överstiga 100 tecken" in str(exc_info.value)

    def test_title_exactly_100_chars_is_valid(self):
        """Test that title with exactly 100 characters is valid."""
        title_100 = "A" * 100
        flash = self.service.create_flash(
            title=title_100,
            content="Valid content here",
            author="Test Author",
        )
        assert len(flash.title) == 100

    def test_content_min_10_chars(self):
        """Test that content must be at least 10 characters (AC3)."""
        with pytest.raises(ValidationError) as exc_info:
            self.service.create_flash(
                title="Valid Title",
                content="Short",  # Only 5 chars
                author="Test Author",
            )
        assert "Innehåll måste vara minst 10 tecken" in str(exc_info.value)

    def test_content_max_5000_chars(self):
        """Test that content cannot exceed 5000 characters (AC3)."""
        long_content = "A" * 5001
        with pytest.raises(ValidationError) as exc_info:
            self.service.create_flash(
                title="Valid Title",
                content=long_content,
                author="Test Author",
            )
        assert "Innehåll får inte överstiga 5000 tecken" in str(exc_info.value)

    def test_content_exactly_10_chars_is_valid(self):
        """Test that content with exactly 10 characters is valid."""
        content_10 = "A" * 10
        flash = self.service.create_flash(
            title="Valid Title",
            content=content_10,
            author="Test Author",
        )
        assert len(flash.content) == 10

    def test_content_exactly_5000_chars_is_valid(self):
        """Test that content with exactly 5000 characters is valid."""
        content_5000 = "A" * 5000
        flash = self.service.create_flash(
            title="Valid Title",
            content=content_5000,
            author="Test Author",
        )
        assert len(flash.content) == 5000


class TestNewsFlashServiceCRUD:
    """Tests for NewsFlash CRUD operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repository = InMemoryNewsFlashRepository()
        self.service = NewsFlashService(repository=self.repository)

    def test_create_flash_returns_newsflash(self):
        """Test that create_flash returns a NewsFlash object."""
        flash = self.service.create_flash(
            title="Test Title",
            content="This is valid content.",
            author="Test Author",
        )

        assert isinstance(flash, NewsFlash)
        assert flash.title == "Test Title"
        assert flash.content == "This is valid content."
        assert flash.author == "Test Author"
        assert flash.id is not None
        assert isinstance(flash.created_at, datetime)

    def test_list_flashes_returns_all(self):
        """Test that list_flashes returns all news flashes."""
        self.service.create_flash(
            title="Flash 1",
            content="Content for flash 1",
            author="Author 1",
        )
        self.service.create_flash(
            title="Flash 2",
            content="Content for flash 2",
            author="Author 2",
        )

        flashes = self.service.list_flashes()
        assert len(flashes) == 2

    def test_get_flash_by_id(self):
        """Test that get_flash returns the correct flash by ID."""
        created = self.service.create_flash(
            title="Test Flash",
            content="Test content here",
            author="Test Author",
        )

        retrieved = self.service.get_flash(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == "Test Flash"

    def test_get_flash_not_found(self):
        """Test that get_flash returns None for non-existent ID."""
        result = self.service.get_flash(999)
        assert result is None

    def test_update_flash(self):
        """Test updating an existing flash."""
        created = self.service.create_flash(
            title="Original Title",
            content="Original content here",
            author="Original Author",
        )

        updated = self.service.update_flash(
            flash_id=created.id,
            title="Updated Title",
            content="Updated content here",
        )

        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.content == "Updated content here"
        assert updated.author == "Original Author"  # Not changed

    def test_update_flash_not_found(self):
        """Test updating a non-existent flash returns None."""
        result = self.service.update_flash(
            flash_id=999,
            title="New Title",
        )
        assert result is None

    def test_update_flash_validates_title(self):
        """Test that update validates title constraints."""
        created = self.service.create_flash(
            title="Original Title",
            content="Original content here",
            author="Author",
        )

        with pytest.raises(ValidationError) as exc_info:
            self.service.update_flash(
                flash_id=created.id,
                title="",  # Empty title
            )
        assert "Titel krävs" in str(exc_info.value)

    def test_update_flash_validates_content(self):
        """Test that update validates content constraints."""
        created = self.service.create_flash(
            title="Original Title",
            content="Original content here",
            author="Author",
        )

        with pytest.raises(ValidationError) as exc_info:
            self.service.update_flash(
                flash_id=created.id,
                content="Short",  # Too short
            )
        assert "Innehåll måste vara minst 10 tecken" in str(exc_info.value)

    def test_delete_flash_success(self):
        """Test deleting an existing flash."""
        created = self.service.create_flash(
            title="To Delete",
            content="Content to delete",
            author="Author",
        )

        result = self.service.delete_flash(created.id)
        assert result is True
        assert self.service.get_flash(created.id) is None

    def test_delete_flash_not_found(self):
        """Test deleting a non-existent flash returns False."""
        result = self.service.delete_flash(999)
        assert result is False

    def test_create_flash_with_published_at(self):
        """Test creating a flash with published_at set."""
        published = datetime(2026, 2, 5, 12, 0, 0)
        flash = self.service.create_flash(
            title="Published Flash",
            content="This is published content",
            author="Author",
            published_at=published,
        )

        assert flash.published_at == published

    def test_update_flash_with_published_at(self):
        """Test updating a flash with published_at."""
        created = self.service.create_flash(
            title="Original Title",
            content="Original content here",
            author="Author",
        )
        published = datetime(2026, 2, 5, 14, 0, 0)

        updated = self.service.update_flash(
            flash_id=created.id,
            published_at=published,
        )

        assert updated is not None
        assert updated.published_at == published

    def test_title_whitespace_only_rejected(self):
        """Test that title with only whitespace is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            self.service.create_flash(
                title="   ",  # Only whitespace
                content="Valid content here",
                author="Test Author",
            )
        assert "Titel krävs" in str(exc_info.value)
