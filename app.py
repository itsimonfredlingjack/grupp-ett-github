"""
Flask application for Agentic Dev Loop demo.

This is a minimal Flask app used to demonstrate the TDD workflow
and test infrastructure of the project.
"""

import os
from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import Flask, Response, jsonify, request
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect

from src.expense_tracker.business.service import ExpenseService
from src.expense_tracker.data.repository import InMemoryExpenseRepository
from src.expense_tracker.presentation.routes import create_expense_blueprint
from src.sejfa.core.admin_auth import AdminAuthService
from src.sejfa.core.subscriber_service import SubscriberService
from src.sejfa.monitor.monitor_routes import (
    create_monitor_blueprint,
    init_socketio_events,
)
from src.sejfa.monitor.monitor_service import MonitorService

# Global SocketIO instance
socketio = None


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        Flask: Configured Flask application instance.
    """
    global socketio

    app = Flask(__name__)
    app.secret_key = os.environ.get(
        "SECRET_KEY", "dev-secret-key"
    )  # In production, use environment variable

    # Initialize CSRF protection
    CSRFProtect(app)

    # Initialize SocketIO for real-time monitoring
    socketio = SocketIO(app, cors_allowed_origins="*")

    # Initialize monitoring service
    monitor_service = MonitorService()

    # Create and register monitoring blueprint
    monitor_blueprint = create_monitor_blueprint(monitor_service, socketio)
    app.register_blueprint(monitor_blueprint)

    # Initialize SocketIO event handlers
    init_socketio_events()

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
        stats = SubscriberService.get_statistics()
        return jsonify({"dashboard": "admin", "statistics": stats}), 200

    @app.route("/admin/statistics", methods=["GET"])
    @require_admin_token
    def admin_statistics():
        """Admin statistics endpoint.

        Returns:
            Response: JSON with statistics data.
        """
        stats = SubscriberService.get_statistics()
        return jsonify(stats), 200

    # Subscriber management endpoints
    @app.route("/admin/subscribers", methods=["GET", "POST"])
    @require_admin_token
    def manage_subscribers():
        """Manage subscribers - list or create.

        Returns:
            Response: JSON with subscriber list or created subscriber.
        """
        if request.method == "GET":
            subscribers = SubscriberService.list_subscribers()
            subscriber_dicts = [
                {
                    "id": s.id,
                    "email": s.email,
                    "name": s.name,
                    "subscribed_date": s.subscribed_date,
                    "active": s.active,
                }
                for s in subscribers
            ]
            return jsonify({"subscribers": subscriber_dicts}), 200

        # POST - Create new subscriber
        data = request.get_json()
        required_fields = {"email", "name", "subscribed_date"}
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        subscriber = SubscriberService.add_subscriber(
            email=data["email"],
            name=data["name"],
            subscribed_date=data["subscribed_date"],
        )
        return jsonify(
            {
                "id": subscriber.id,
                "email": subscriber.email,
                "name": subscriber.name,
                "subscribed_date": subscriber.subscribed_date,
                "active": subscriber.active,
            }
        ), 201

    @app.route(
        "/admin/subscribers/<int:subscriber_id>", methods=["GET", "PUT", "DELETE"]
    )
    @require_admin_token
    def manage_subscriber(subscriber_id: int):
        """Manage a specific subscriber - get, update, or delete.

        Args:
            subscriber_id: Subscriber ID.

        Returns:
            Response: JSON with subscriber data or status.
        """
        if request.method == "GET":
            subscriber = SubscriberService.get_subscriber(subscriber_id)
            if not subscriber:
                return jsonify({"error": "Subscriber not found"}), 404
            return jsonify(
                {
                    "id": subscriber.id,
                    "email": subscriber.email,
                    "name": subscriber.name,
                    "subscribed_date": subscriber.subscribed_date,
                    "active": subscriber.active,
                }
            ), 200

        if request.method == "PUT":
            subscriber = SubscriberService.get_subscriber(subscriber_id)
            if not subscriber:
                return jsonify({"error": "Subscriber not found"}), 404

            data = request.get_json()
            updated = SubscriberService.update_subscriber(
                subscriber_id,
                email=data.get("email"),
                name=data.get("name"),
                active=data.get("active"),
            )
            if not updated:
                return jsonify({"error": "Failed to update subscriber"}), 400

            return jsonify(
                {
                    "id": updated.id,
                    "email": updated.email,
                    "name": updated.name,
                    "subscribed_date": updated.subscribed_date,
                    "active": updated.active,
                }
            ), 200

        if request.method == "DELETE":
            deleted = SubscriberService.delete_subscriber(subscriber_id)
            if not deleted:
                return jsonify({"error": "Subscriber not found"}), 404
            return jsonify({"message": "Subscriber deleted"}), 204

    @app.route("/admin/subscribers/search", methods=["GET"])
    @require_admin_token
    def search_subscribers():
        """Search subscribers by email or name.

        Returns:
            Response: JSON with search results.
        """
        query = request.args.get("q", "")
        if not query:
            return jsonify({"error": "Missing search query"}), 400

        results = SubscriberService.search_subscribers(query)
        result_dicts = [
            {
                "id": s.id,
                "email": s.email,
                "name": s.name,
                "subscribed_date": s.subscribed_date,
                "active": s.active,
            }
            for s in results
        ]
        return jsonify({"results": result_dicts}), 200

    @app.route("/admin/subscribers/export", methods=["GET"])
    @require_admin_token
    def export_subscribers():
        """Export subscribers as CSV.

        Returns:
            Response: CSV file.
        """
        csv_data = SubscriberService.export_csv()
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=subscribers.csv"},
        )

    # Register ExpenseTracker blueprint with DI
    expense_repository = InMemoryExpenseRepository()
    expense_service = ExpenseService(expense_repository)
    expense_blueprint = create_expense_blueprint(expense_service)
    app.register_blueprint(expense_blueprint, url_prefix="/expenses")

    return app


# Create app instance for direct running
app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000, host="0.0.0.0", allow_unsafe_werkzeug=True)
