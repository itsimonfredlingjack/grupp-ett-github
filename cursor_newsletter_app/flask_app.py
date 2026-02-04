"""Flask application factory and initialization."""
from pathlib import Path

from flask import Flask

from cursor_newsletter_app.repository import InMemoryRepository
from cursor_newsletter_app.service import NewsService


def create_app(config: dict | None = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config: Optional configuration dictionary.

    Returns:
        Configured Flask application instance.
    """
    template_path = Path(__file__).parent / "templates"
    app = Flask(__name__, template_folder=str(template_path))

    # Apply configuration
    if config:
        app.config.update(config)
    else:
        app.config["TESTING"] = False

    # Dependency injection: create repository and service
    repository = InMemoryRepository()
    news_service = NewsService(repository)

    # Store service in app config for access in routes
    app.config["NEWS_SERVICE"] = news_service

    # Register blueprint
    from cursor_newsletter_app.routes import create_blueprint

    blueprint = create_blueprint(news_service)
    app.register_blueprint(blueprint)

    return app
