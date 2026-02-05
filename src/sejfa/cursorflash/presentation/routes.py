"""Flask routes for Cursorflash."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.sejfa.cursorflash.business.service import FlashService, ValidationError


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

    return bp
