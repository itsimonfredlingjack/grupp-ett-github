"""
Flask application for Agentic Dev Loop demo.

This is a minimal Flask app used to demonstrate the TDD workflow
and test infrastructure of the project.
"""

from flask import Flask, jsonify


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)

    @app.route("/")
    def hello():
        """Root endpoint returning a greeting.

        Returns:
            Response: JSON response with greeting message.
        """
        return jsonify({"message": "Hello, Agentic Dev Loop!"})

    @app.route("/health")
    def health():
        """Health check endpoint.

        Returns:
            Response: JSON response with health status.
        """
        return jsonify({"status": "healthy"})

    return app


# Create app instance for direct running
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
