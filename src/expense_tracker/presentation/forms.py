from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField
from wtforms.validators import DataRequired, NumberRange


class ExpenseForm(FlaskForm):
    """Form for adding new expenses."""

    title = StringField("Titel", validators=[DataRequired()])
    amount = DecimalField("Belopp", validators=[DataRequired(), NumberRange(min=0.01)])
    category = SelectField(
        "Kategori",
        choices=[
            ("", "Välj kategori..."),
            ("Mat", "Mat"),
            ("Transport", "Transport"),
            ("Boende", "Boende"),
            ("Övrigt", "Övrigt"),
        ],
        validators=[DataRequired()],
    )
