"""Flask routes for News Flash newsletter."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.sejfa.newsflash.business.subscription_service import (
    SubscriptionService,
    ValidationError,
)


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
        """Handle subscription form submission with validation.

        Returns:
            Rendered thank you template on success, or subscribe form with
            error message on validation failure.
        """
        subscription_service = SubscriptionService()

        email = request.form.get("email", "")
        name = request.form.get("name", "")

        try:
            # Process subscription with validation and normalization
            result = subscription_service.process_subscription(email, name)

            # Success - redirect to thank you page
            flash(f"Tack för din prenumeration, {result['name']}!", "success")
            return redirect(url_for("newsflash.subscribe"))

        except ValidationError as e:
            # Validation failed - re-render form with error and preserved input
            return render_template(
                "newsflash/subscribe.html",
                error=str(e),
                email_value=email,
                name_value=name,
            )

    return bp
