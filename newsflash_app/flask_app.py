"""Flask application factory."""

from flask import Flask

from newsflash_app.business.service import NewsFlashService
from newsflash_app.data.repository import InMemoryNewsFlashRepository
from newsflash_app.presentation.routes import create_blueprint


def create_app(config: dict | None = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config: Optional configuration dictionary.

    Returns:
        Configured Flask app instance.
    """
    app = Flask(__name__, template_folder="presentation/templates")

    if config:
        app.config.update(config)

    # Dependency injection: create repository and service
    repository = InMemoryNewsFlashRepository()
    service = NewsFlashService(repository)

    # Register blueprint with injected service
    blueprint = create_blueprint(service)
    app.register_blueprint(blueprint)

    return app
