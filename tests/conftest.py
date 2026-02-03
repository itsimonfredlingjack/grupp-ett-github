"""Global test configuration and fixtures."""

import pytest

from src.sejfa.core.admin_auth import AdminAuthService


@pytest.fixture(autouse=True)
def setup_auth_credentials(monkeypatch):
    """Set default admin credentials for all tests.

    This ensures that AdminAuthService has valid credentials configured
    even though the default values were removed from the source code.
    """
    monkeypatch.setattr(
        AdminAuthService,
        "VALID_ADMIN",
        {"username": "admin", "password": "admin123"},
    )
