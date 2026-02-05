"""Health check utilities for SEJFA application."""

from datetime import datetime, timezone


def health_check() -> dict[str, str]:
    """Return health check status with current timestamp.

    Returns:
        dict: Dictionary containing:
            - status: 'ok' indicating the service is healthy
            - timestamp: Current UTC timestamp in ISO 8601 format
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
