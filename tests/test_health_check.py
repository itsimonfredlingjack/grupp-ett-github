"""Tests for health check functionality."""

from datetime import datetime

from src.sejfa.utils.health import health_check


def test_health_check_returns_status_ok():
    """Test that health_check returns status 'ok'."""
    result = health_check()
    assert result["status"] == "ok"


def test_health_check_returns_timestamp():
    """Test that health_check returns current timestamp."""
    result = health_check()
    assert "timestamp" in result

    # Verify timestamp is in ISO 8601 format
    timestamp_str = result["timestamp"]
    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

    # Timestamp should be recent (within last 5 seconds)
    now = datetime.now(timestamp.tzinfo)
    time_diff = abs((now - timestamp).total_seconds())
    assert time_diff < 5, f"Timestamp is not recent: {time_diff}s difference"


def test_health_check_returns_both_fields():
    """Test that health_check returns both status and timestamp."""
    result = health_check()
    assert "status" in result
    assert "timestamp" in result
    assert len(result) == 2  # Only these two fields
