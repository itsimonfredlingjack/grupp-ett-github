"""Data models for the news flash application."""

from dataclasses import dataclass


VALID_CATEGORIES = {"BREAKING", "TECH", "FINANCE", "SPORTS"}


@dataclass
class NewsFlash:
    """Represents a news flash item."""

    id: int
    headline: str
    summary: str
    category: str

    def __post_init__(self) -> None:
        """Validate business rules."""
        if len(self.headline) <= 5:
            raise ValueError("Rubrik måste vara längre än 5 tecken")

        if self.category not in VALID_CATEGORIES:
            raise ValueError(
                f"Kategori måste vara en av: {', '.join(sorted(VALID_CATEGORIES))}"
            )
