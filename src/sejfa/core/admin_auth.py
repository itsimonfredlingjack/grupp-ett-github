"""Admin authentication module."""

import os
import secrets
from dataclasses import dataclass
from hmac import compare_digest


@dataclass
class AdminCredentials:
    """Admin login credentials."""

    username: str
    password: str


class AdminAuthService:
    """Service for handling admin authentication."""

    _active_tokens: set[str] = set()

    @staticmethod
    def _get_admin_credentials() -> AdminCredentials | None:
        username = os.getenv("ADMIN_USERNAME", "").strip()
        password = os.getenv("ADMIN_PASSWORD", "").strip()
        if not username or not password:
            return None
        return AdminCredentials(username=username, password=password)

    @staticmethod
    def authenticate(username: str, password: str) -> bool:
        """Authenticate admin credentials.

        Args:
            username: Admin username.
            password: Admin password.

        Returns:
            bool: True if credentials are valid.
        """
        credentials = AdminAuthService._get_admin_credentials()
        if credentials is None:
            return False
        return compare_digest(username, credentials.username) and compare_digest(
            password, credentials.password
        )

    @staticmethod
    def generate_session_token(username: str) -> str:
        """Generate a session token for authenticated admin.

        Args:
            username: Authenticated admin username.

        Returns:
            str: Session token.
        """
        token = f"token_{secrets.token_urlsafe(24)}"
        AdminAuthService._active_tokens.add(token)
        return token

    @staticmethod
    def validate_session_token(token: str | None) -> bool:
        """Validate a session token.

        Args:
            token: Session token to validate.

        Returns:
            bool: True if token is valid.
        """
        return token is not None and token in AdminAuthService._active_tokens
