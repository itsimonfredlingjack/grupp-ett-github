"""Flask routes for News Flash newsletter."""

from flask import Blueprint, render_template, request


def create_newsflash_blueprint() -> Blueprint:
    """Create News Flash blueprint.

    Returns:
        Configured Flask Blueprint for News Flash newsletter.
    """
    bp = Blueprint(
        "newsflash",
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/static/newsflash",
    )

    @bp.route("/")
    def index() -> str:
        """Display News Flash landing page with hero section.

        Returns:
            Rendered index template.
        """
        return render_template("newsflash/index.html")

    @bp.route("/subscribe")
    def subscribe() -> str:
        """Display subscription form.

        Returns:
            Rendered subscribe template.
        """
        return render_template("newsflash/subscribe.html")

    @bp.route("/subscribe/confirm", methods=["POST"])
    def subscribe_confirm() -> str:
        """Handle subscription form submission.

        Returns:
            Rendered thank you template with submitted data.
        """
        email = request.form.get("email", "")
        name = request.form.get("name", "")
        return render_template("newsflash/thank_you.html", email=email, name=name)

    return bp
