"""Tests for Cursorflash business layer."""

from __future__ import annotations

import pytest

from src.sejfa.cursorflash.business.service import FlashService, ValidationError
from src.sejfa.cursorflash.data.repository import InMemoryFlashRepository


class TestFlashServiceValidation:
    """Test FlashService validation rules."""

    def test_empty_content_raises_error(self) -> None:
        """Test that empty content raises ValidationError."""
        repo = InMemoryFlashRepository()
        service = FlashService(repo)

        with pytest.raises(ValidationError) as exc_info:
            service.create_flash("", severity=3)

        assert "tomt" in str(exc_info.value).lower()

    def test_content_too_long_raises_error(self) -> None:
        """Test that content over 280 chars raises ValidationError."""
        repo = InMemoryFlashRepository()
        service = FlashService(repo)
        long_content = "x" * 281

        with pytest.raises(ValidationError) as exc_info:
            service.create_flash(long_content, severity=3)

        assert "280" in str(exc_info.value)

    def test_content_exactly_280_chars_allowed(self) -> None:
        """Test that content with exactly 280 chars is allowed."""
        repo = InMemoryFlashRepository()
        service = FlashService(repo)
        exact_content = "x" * 280

        flash = service.create_flash(exact_content, severity=3)
        assert flash.content == exact_content

    def test_severity_below_1_raises_error(self) -> None:
        """Test that severity < 1 raises ValidationError."""
        repo = InMemoryFlashRepository()
        service = FlashService(repo)

        with pytest.raises(ValidationError) as exc_info:
            service.create_flash("Valid content", severity=0)

        assert "1" in str(exc_info.value) and "5" in str(exc_info.value)

    def test_severity_above_5_raises_error(self) -> None:
        """Test that severity > 5 raises ValidationError."""
        repo = InMemoryFlashRepository()
        service = FlashService(repo)

        with pytest.raises(ValidationError) as exc_info:
            service.create_flash("Valid content", severity=6)

        assert "1" in str(exc_info.value) and "5" in str(exc_info.value)

    def test_severity_1_is_valid(self) -> None:
        """Test that severity 1 is valid."""
        repo = InMemoryFlashRepository()
        service = FlashService(repo)

        flash = service.create_flash("Test", severity=1)
        assert flash.severity == 1

    def test_severity_5_is_valid(self) -> None:
        """Test that severity 5 is valid."""
        repo = InMemoryFlashRepository()
        service = FlashService(repo)

        flash = service.create_flash("Test", severity=5)
        assert flash.severity == 5


class TestFlashServiceOperations:
    """Test FlashService CRUD operations."""

    def test_create_flash_returns_flash_with_id(self) -> None:
        """Test creating a flash returns it with assigned ID."""
        repo = InMemoryFlashRepository()
        service = FlashService(repo)

        flash = service.create_flash("Breaking news!", severity=3)

        assert flash.id > 0
        assert flash.content == "Breaking news!"
        assert flash.severity == 3

    def test_get_all_flashes_empty(self) -> None:
        """Test getting all flashes when none exist."""
        repo = InMemoryFlashRepository()
        service = FlashService(repo)

        flashes = service.get_all_flashes()
        assert flashes == []

    def test_get_all_flashes_returns_created_flashes(self) -> None:
        """Test getting all flashes returns created ones."""
        repo = InMemoryFlashRepository()
        service = FlashService(repo)

        flash1 = service.create_flash("First", severity=1)
        flash2 = service.create_flash("Second", severity=5)

        flashes = service.get_all_flashes()
        assert len(flashes) == 2
        assert flash1 in flashes
        assert flash2 in flashes

    def test_clear_flashes(self) -> None:
        """Test clearing all flashes."""
        repo = InMemoryFlashRepository()
        service = FlashService(repo)

        service.create_flash("Test", severity=3)
        service.clear_flashes()

        assert service.get_all_flashes() == []


class TestFlashServiceDependencyInjection:
    """Test FlashService dependency injection."""

    def test_service_uses_injected_repository(self) -> None:
        """Test that service uses the injected repository."""
        repo = InMemoryFlashRepository()
        service = FlashService(repo)

        flash = service.create_flash("Test", severity=2)

        # Verify the flash is in the repository
        assert flash in repo.get_all()
