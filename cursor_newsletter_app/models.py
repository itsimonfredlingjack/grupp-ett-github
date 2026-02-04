"""Data models for the newsletter application."""

from dataclasses import dataclass


@dataclass
class NewsItem:
    """Represents a news headline item."""

    id: int
    title: str
    content: str

    def __post_init__(self) -> None:
        """Validate business rules."""
        if len(self.title) <= 3:
            raise ValueError("Titel måste vara längre än 3 tecken")
