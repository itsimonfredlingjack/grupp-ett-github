"""Flask application factory for Cursorflash."""

from __future__ import annotations

from flask import Flask

from src.sejfa.cursorflash.business.service import FlashService
from src.sejfa.cursorflash.data.repository import InMemoryFlashRepository
from src.sejfa.cursorflash.presentation.routes import create_blueprint


def create_app() -> Flask:
    """Create and configure the Flask application.

    This factory assembles the 3-layer architecture:
    1. Data Layer: InMemoryFlashRepository
    2. Business Layer: FlashService (with injected repository)
    3. Presentation Layer: Flask Blueprint

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key-for-flashing"

    # Layer 1: Data
    repository = InMemoryFlashRepository()

    # Layer 2: Business (inject repository)
    service = FlashService(repository)

    # Layer 3: Presentation (inject service)
    blueprint = create_blueprint(service)
    app.register_blueprint(blueprint, url_prefix="/cursorflash")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5001)
