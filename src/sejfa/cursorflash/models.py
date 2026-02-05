"""Data models for Cursorflash."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewsFlash:
    """NewsFlash data model.

    Represents a news flash with all required fields.

    Attributes:
        id: Unique identifier.
        title: Title of the news flash.
        content: Content body of the news flash.
        created_at: When the flash was created.
        author: Author of the flash.
        published_at: When the flash was published (optional).
    """

    id: int
    title: str
    content: str
    created_at: datetime
    author: str
    published_at: datetime | None = None
