"""Repository for News Flash subscriber data access."""

from __future__ import annotations

from src.sejfa.newsflash.data.models import Subscriber, db


class SubscriberRepository:
    """Repository for Subscriber persistence via SQLAlchemy.

    Provides find_by_email(), exists(), and create() methods
    for subscriber data access.
    """

    def find_by_email(self, email: str) -> Subscriber | None:
        """Find a subscriber by email address.

        Args:
            email: Email address to search for.

        Returns:
            Subscriber if found, None otherwise.
        """
        return db.session.execute(
            db.select(Subscriber).filter_by(email=email)
        ).scalar_one_or_none()

    def exists(self, email: str) -> bool:
        """Check if a subscriber with the given email exists.

        Args:
            email: Email address to check.

        Returns:
            True if subscriber exists, False otherwise.
        """
        return self.find_by_email(email) is not None

    def create(self, email: str, name: str) -> Subscriber:
        """Create a new subscriber.

        Args:
            email: Subscriber email address.
            name: Subscriber name.

        Returns:
            The created Subscriber instance.
        """
        subscriber = Subscriber(email=email, name=name)
        db.session.add(subscriber)
        db.session.commit()
        return subscriber
