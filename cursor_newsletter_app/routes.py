"""Flask routes for the newsletter application."""
from flask import Blueprint, redirect, render_template, request, url_for

from cursor_newsletter_app.service import NewsService


def create_blueprint(service: NewsService) -> Blueprint:
    """Create and configure the blueprint with dependency injection.

    Args:
        service: The NewsService instance.

    Returns:
        Configured Flask Blueprint.
    """
    bp = Blueprint("main", __name__)

    @bp.route("/", methods=["GET"])
    def index():
        """Render the main page with all news items."""
        items = service.get_news()
        return render_template("index.html", news_items=items)

    @bp.route("/add", methods=["POST"])
    def add():
        """Add a new news item."""
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        try:
            service.create_news(title, content)
            return redirect(url_for("main.index"))
        except ValueError as e:
            return render_template("error.html", message=str(e)), 400

    @bp.route("/delete/<int:item_id>", methods=["GET"])
    def delete(item_id: int):
        """Delete a news item."""
        service.delete_news(item_id)
        return redirect(url_for("main.index"))

    return bp
