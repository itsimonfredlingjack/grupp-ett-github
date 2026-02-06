"""Flask routes for Cursorflash."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.sejfa.cursorflash.business.service import FlashService, ValidationError
from src.sejfa.cursorflash.business.subscription_service import SubscriptionService


def create_blueprint(flash_service: FlashService) -> Blueprint:
    """Create Cursorflash blueprint with injected service.

    Args:
        flash_service: FlashService instance

    Returns:
        Configured Flask Blueprint
    """
    bp = Blueprint("cursorflash", __name__, template_folder="templates")

    @bp.route("/")
    def index() -> str:
        """Display main page with form and flash list."""
        flashes = flash_service.get_all_flashes()
        return render_template("cursorflash/index.html", flashes=flashes)

    @bp.route("/add", methods=["POST"])
    def add() -> str:
        """Handle flash creation from form."""
        content = request.form.get("content", "").strip()
        severity_str = request.form.get("severity", "")

        try:
            severity = int(severity_str)
            flash_service.create_flash(content, severity)
            flash("Flash tillagd!", "success")
        except ValueError:
            flash("Felaktig allvarlighetsgrad", "error")
        except ValidationError as e:
            flash(str(e), "error")

        return redirect(url_for("cursorflash.index"))

    @bp.route("/clear")
    def clear() -> str:
        """Clear all flashes (dev route)."""
        flash_service.clear_flashes()
        flash("Alla flashes rensade", "info")
        return redirect(url_for("cursorflash.index"))

    @bp.route("/subscribe/confirm", methods=["POST"])
    def subscribe_confirm() -> str:
        """Handle subscription form submission."""
        subscription_service = SubscriptionService()

        email = request.form.get("email", "")
        name = request.form.get("name", "")

        try:
            # Process subscription with validation and normalization
            result = subscription_service.process_subscription(email, name)

            # Success - redirect with success message
            flash(
                f"Tack för din prenumeration, {result['name']}!",
                "success"
            )
            return redirect(url_for("cursorflash.index"))

        except ValidationError as e:
            # Validation failed - re-render form with error and preserved input
            flashes = flash_service.get_all_flashes()
            return render_template(
                "cursorflash/index.html",
                flashes=flashes,
                subscription_error=str(e),
                email_value=email,
                name_value=name,
            )

    return bp
