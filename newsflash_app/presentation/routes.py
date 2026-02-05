"""Flask routes for the news flash application."""

from flask import Blueprint, redirect, render_template, request, url_for

from newsflash_app.business.service import NewsFlashService


def create_blueprint(service: NewsFlashService) -> Blueprint:
    """Create and configure the blueprint with dependency injection.

    Args:
        service: The NewsFlashService instance.

    Returns:
        Configured Flask Blueprint.
    """
    bp = Blueprint("main", __name__)

    @bp.route("/", methods=["GET"])
    def index():
        """Render the main page with all news flash items."""
        flashes = service.get_all_flashes()
        return render_template("index.html", flashes=flashes)

    @bp.route("/add", methods=["POST"])
    def add():
        """Add a new news flash item."""
        headline = request.form.get("headline", "").strip()
        summary = request.form.get("summary", "").strip()
        category = request.form.get("category", "").strip()

        try:
            service.create_flash(headline, summary, category)
            return redirect(url_for("main.index"))
        except ValueError as e:
            return render_template("error.html", message=str(e)), 400

    @bp.route("/delete/<int:item_id>", methods=["GET"])
    def delete(item_id: int):
        """Delete a news flash item."""
        service.delete_flash(item_id)
        return redirect(url_for("main.index"))

    return bp
