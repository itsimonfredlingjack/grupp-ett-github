"""Flask Blueprint for ExpenseTracker routes.

This module handles HTTP requests and delegates to the business service.
"""

from flask import Blueprint, flash, redirect, render_template, url_for

from src.expense_tracker.business.exceptions import ExpenseValidationError
from src.expense_tracker.business.service import ExpenseService
from src.expense_tracker.presentation.forms import ExpenseForm


def create_expense_blueprint(service: ExpenseService) -> Blueprint:
    """Create a Flask Blueprint for expense tracker routes.

    Uses dependency injection to receive the service instance.

    Args:
        service: The ExpenseService to use for business operations.

    Returns:
        Configured Flask Blueprint.
    """
    bp = Blueprint(
        "expense_tracker",
        __name__,
        template_folder="../templates",
    )

    @bp.route("/")
    def index():
        """List all expenses."""
        expenses = service.get_all_expenses()
        form = ExpenseForm()
        return render_template(
            "expense_tracker/index.html", expenses=expenses, form=form
        )

    @bp.route("/add", methods=["POST"])
    def add_expense():
        """Add a new expense from form data."""
        form = ExpenseForm()
        if form.validate_on_submit():
            try:
                service.add_expense(
                    title=form.title.data,
                    amount=form.amount.data,
                    category=form.category.data,
                )
                flash("Utgift tillagd! (Expense added)", "success")
            except ExpenseValidationError as e:
                flash(str(e), "error")
        else:
            for _, errors in form.errors.items():
                for error in errors:
                    flash(f"{error}", "error")

        return redirect(url_for("expense_tracker.index"))

    @bp.route("/summary")
    def summary():
        """Show summary with total amount."""
        total = service.get_total_amount()
        return render_template("expense_tracker/summary.html", total=total)

    return bp
