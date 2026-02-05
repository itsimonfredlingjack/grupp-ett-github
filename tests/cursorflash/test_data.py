"""Tests for Cursorflash data layer."""

from __future__ import annotations

from src.sejfa.cursorflash.data.models import Flash
from src.sejfa.cursorflash.data.repository import InMemoryFlashRepository


class TestFlashModel:
    """Test Flash dataclass."""

    def test_flash_creation(self) -> None:
        """Test creating a Flash instance."""
        flash = Flash(id=1, content="Breaking news!", severity=3)
        assert flash.id == 1
        assert flash.content == "Breaking news!"
        assert flash.severity == 3

    def test_flash_equality(self) -> None:
        """Test Flash equality comparison."""
        flash1 = Flash(id=1, content="News", severity=2)
        flash2 = Flash(id=1, content="News", severity=2)
        assert flash1 == flash2


class TestInMemoryFlashRepository:
    """Test InMemoryFlashRepository."""

    def test_add_flash(self) -> None:
        """Test adding a flash to repository."""
        repo = InMemoryFlashRepository()
        flash = Flash(id=1, content="Test flash", severity=2)
        result = repo.add(flash)
        assert result == flash

    def test_get_all_empty(self) -> None:
        """Test getting all flashes when empty."""
        repo = InMemoryFlashRepository()
        flashes = repo.get_all()
        assert flashes == []

    def test_get_all_returns_flashes(self) -> None:
        """Test getting all flashes after adding some."""
        repo = InMemoryFlashRepository()
        flash1 = Flash(id=1, content="First", severity=1)
        flash2 = Flash(id=2, content="Second", severity=5)
        repo.add(flash1)
        repo.add(flash2)

        flashes = repo.get_all()
        assert len(flashes) == 2
        assert flash1 in flashes
        assert flash2 in flashes

    def test_clear(self) -> None:
        """Test clearing all flashes."""
        repo = InMemoryFlashRepository()
        repo.add(Flash(id=1, content="Test", severity=3))
        repo.add(Flash(id=2, content="Test2", severity=4))

        repo.clear()
        assert repo.get_all() == []

    def test_auto_increment_id(self) -> None:
        """Test that repository auto-assigns IDs."""
        repo = InMemoryFlashRepository()
        flash1 = Flash(id=0, content="First", severity=1)
        flash2 = Flash(id=0, content="Second", severity=2)

        result1 = repo.add(flash1)
        result2 = repo.add(flash2)

        assert result1.id == 1
        assert result2.id == 2
