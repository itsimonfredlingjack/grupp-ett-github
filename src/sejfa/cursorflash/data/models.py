"""Data models for Cursorflash."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Flash:
    """A news flash.

    Attributes:
        id: Unique identifier (auto-assigned by repository)
        content: The flash message content
        severity: Severity level (1-5)
    """

    id: int
    content: str
    severity: int
