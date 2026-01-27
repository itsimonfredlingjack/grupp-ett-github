"""
Flask application for Agentic Dev Loop demo.

This is a minimal Flask app used to demonstrate the TDD workflow
and test infrastructure of the project.
"""

from functools import wraps
from typing import Any, Callable

from flask import Flask, jsonify, request

from src.grupp_ett.admin_auth import AdminAuthService


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)
    app.secret_key = "dev-secret-key"  # In production, use environment variable

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

    # Admin authentication routes
    @app.route("/admin/login", methods=["POST"])
    def admin_login():
        """Admin login endpoint.

        Expects JSON with username and password.

        Returns:
            Response: JSON with token or error message.
        """
        data = request.get_json()

        if not data or "username" not in data or "password" not in data:
            return jsonify({"error": "Missing username or password"}), 400

        username = data.get("username")
        password = data.get("password")

        if AdminAuthService.authenticate(username, password):
            token = AdminAuthService.generate_session_token(username)
            return jsonify({"token": token, "username": username}), 200

        return jsonify({"error": "Invalid credentials"}), 401

    def require_admin_token(f: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator to require admin authentication token.

        Args:
            f: Route function to decorate.

        Returns:
            Callable: Decorated function.
        """

        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            token = None

            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]  # Remove "Bearer " prefix

            if not AdminAuthService.validate_session_token(token):
                return jsonify({"error": "Unauthorized"}), 401

            return f(*args, **kwargs)

        return decorated_function

    @app.route("/admin", methods=["GET"])
    @require_admin_token
    def admin_dashboard():
        """Admin dashboard endpoint.

        Returns:
            Response: JSON with dashboard data.
        """
        return jsonify({
            "dashboard": "admin",
            "subscribers_count": 0,
            "statistics": {}
        }), 200

    return app


# Create app instance for direct running
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
