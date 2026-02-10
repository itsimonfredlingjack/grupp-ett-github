"""Admin authentication module."""

import os
from dataclasses import dataclass


@dataclass
class AdminCredentials:
    """Admin login credentials."""

    username: str
    password: str


class AdminAuthService:
    """Service for handling admin authentication."""

    @staticmethod
    def _get_admin_credentials() -> dict[str, str]:
        """Get admin credentials from environment variables."""
        return {
            "username": os.environ.get("ADMIN_USERNAME", "admin"),
            "password": os.environ.get("ADMIN_PASSWORD", "admin123"),
        }

    @staticmethod
    def authenticate(username: str, password: str) -> bool:
        """Authenticate admin credentials.

        Args:
            username: Admin username.
            password: Admin password.

        Returns:
            bool: True if credentials are valid.
        """
        creds = AdminAuthService._get_admin_credentials()
        return (
            username == creds["username"]
            and password == creds["password"]
        )

    @staticmethod
    def generate_session_token(username: str) -> str:
        """Generate a session token for authenticated admin.

        Args:
            username: Authenticated admin username.

        Returns:
            str: Session token.
        """
        # Simple token generation (in production, use JWT or secure sessions)
        return f"token_{username}_{hash(username) % 10000}"

    @staticmethod
    def validate_session_token(token: str | None) -> bool:
        """Validate a session token.

        Args:
            token: Session token to validate.

        Returns:
            bool: True if token is valid.
        """
        return token is not None and token.startswith("token_")
