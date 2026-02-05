"""Tests for NewsFlash data model."""

from datetime import datetime

from src.sejfa.cursorflash.models import NewsFlash


class TestNewsFlashModel:
    """Tests for NewsFlash dataclass."""

    def test_create_newsflash_with_required_fields(self):
        """Test creating a NewsFlash with all required fields."""
        flash = NewsFlash(
            id=1,
            title="Viktig nyhet",
            content="Detta är innehållet i nyhetsflashen.",
            created_at=datetime(2026, 2, 5, 10, 0, 0),
            author="Test Author",
        )

        assert flash.id == 1
        assert flash.title == "Viktig nyhet"
        assert flash.content == "Detta är innehållet i nyhetsflashen."
        assert flash.created_at == datetime(2026, 2, 5, 10, 0, 0)
        assert flash.author == "Test Author"
        assert flash.published_at is None  # Optional field

    def test_create_newsflash_with_published_at(self):
        """Test creating a NewsFlash with published_at set."""
        created = datetime(2026, 2, 5, 10, 0, 0)
        published = datetime(2026, 2, 5, 12, 0, 0)

        flash = NewsFlash(
            id=1,
            title="Publicerad nyhet",
            content="Detta är en publicerad nyhet.",
            created_at=created,
            published_at=published,
            author="Test Author",
        )

        assert flash.published_at == published

    def test_newsflash_fields_types(self):
        """Test that NewsFlash has correct field types."""
        flash = NewsFlash(
            id=1,
            title="Test",
            content="Test content here",
            created_at=datetime.now(),
            author="Author",
        )

        assert isinstance(flash.id, int)
        assert isinstance(flash.title, str)
        assert isinstance(flash.content, str)
        assert isinstance(flash.created_at, datetime)
        assert isinstance(flash.author, str)
