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


class TestSubscriptionServiceEmailValidation:
    """Test SubscriptionService email validation."""

    def test_validate_empty_email_returns_false_with_error(self) -> None:
        """Test that empty email returns (False, 'Email is required')."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        valid, message = service.validate_email("")

        assert valid is False
        assert message == "Email is required"

    def test_validate_none_email_returns_false_with_error(self) -> None:
        """Test that None email returns (False, 'Email is required')."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        valid, message = service.validate_email(None)

        assert valid is False
        assert message == "Email is required"

    def test_validate_invalid_email_returns_false_with_error(self) -> None:
        """Test that invalid email returns (False, 'Invalid email format')."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        valid, message = service.validate_email("invalid")

        assert valid is False
        assert message == "Invalid email format"

    def test_validate_invalid_email_no_at_sign(self) -> None:
        """Test that email without @ is invalid."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        valid, message = service.validate_email("notanemail.com")

        assert valid is False
        assert message == "Invalid email format"

    def test_validate_invalid_email_no_domain(self) -> None:
        """Test that email without domain is invalid."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        valid, message = service.validate_email("user@")

        assert valid is False
        assert message == "Invalid email format"

    def test_validate_valid_email_returns_true(self) -> None:
        """Test that valid email returns (True, '')."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        valid, message = service.validate_email("test@example.com")

        assert valid is True
        assert message == ""

    def test_validate_valid_email_with_subdomain(self) -> None:
        """Test that valid email with subdomain is accepted."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        valid, message = service.validate_email("user@mail.example.com")

        assert valid is True
        assert message == ""


class TestSubscriptionServiceNormalization:
    """Test SubscriptionService normalization methods."""

    def test_normalize_email_lowercase(self) -> None:
        """Test that normalize_email converts to lowercase."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        normalized = service.normalize_email("TEST@EXAMPLE.COM")

        assert normalized == "test@example.com"

    def test_normalize_email_strip_whitespace(self) -> None:
        """Test that normalize_email strips whitespace."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        normalized = service.normalize_email("  test@example.com  ")

        assert normalized == "test@example.com"

    def test_normalize_email_both_lowercase_and_strip(self) -> None:
        """Test that normalize_email does both lowercase and strip."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        normalized = service.normalize_email("  TEST@EXAMPLE.COM  ")

        assert normalized == "test@example.com"

    def test_normalize_name_strip_whitespace(self) -> None:
        """Test that normalize_name strips whitespace."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        normalized = service.normalize_name("  John Doe  ")

        assert normalized == "John Doe"

    def test_normalize_name_empty_returns_default(self) -> None:
        """Test that normalize_name returns 'Subscriber' for empty string."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        normalized = service.normalize_name("")

        assert normalized == "Subscriber"

    def test_normalize_name_none_returns_default(self) -> None:
        """Test that normalize_name returns 'Subscriber' for None."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        normalized = service.normalize_name(None)

        assert normalized == "Subscriber"

    def test_normalize_name_whitespace_only_returns_default(self) -> None:
        """Test that normalize_name returns 'Subscriber' for whitespace-only."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        normalized = service.normalize_name("   ")

        assert normalized == "Subscriber"


class TestSubscriptionServiceProcessing:
    """Test SubscriptionService process_subscription method."""

    def test_process_subscription_with_valid_data(self) -> None:
        """Test process_subscription with valid email and name."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        result = service.process_subscription("TEST@EXAMPLE.COM", "John Doe")

        assert result["email"] == "test@example.com"
        assert result["name"] == "John Doe"
        assert "subscribed_at" in result

    def test_process_subscription_normalizes_email(self) -> None:
        """Test that process_subscription normalizes email."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        result = service.process_subscription("  TEST@EXAMPLE.COM  ", "John")

        assert result["email"] == "test@example.com"

    def test_process_subscription_normalizes_name(self) -> None:
        """Test that process_subscription normalizes name."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        result = service.process_subscription("test@example.com", "  John  ")

        assert result["name"] == "John"

    def test_process_subscription_empty_name_uses_default(self) -> None:
        """Test that process_subscription uses 'Subscriber' for empty name."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()
        result = service.process_subscription("test@example.com", "")

        assert result["name"] == "Subscriber"

    def test_process_subscription_invalid_email_raises_error(self) -> None:
        """Test that process_subscription raises error for invalid email."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()

        with pytest.raises(ValidationError) as exc_info:
            service.process_subscription("invalid", "John")

        assert "Invalid email format" in str(exc_info.value)

    def test_process_subscription_empty_email_raises_error(self) -> None:
        """Test that process_subscription raises error for empty email."""
        from src.sejfa.cursorflash.business.subscription_service import (
            SubscriptionService,
        )

        service = SubscriptionService()

        with pytest.raises(ValidationError) as exc_info:
            service.process_subscription("", "John")

        assert "Email is required" in str(exc_info.value)
