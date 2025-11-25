# File: app/forms/feedback_form.py

from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField, HiddenField
from wtforms.validators import DataRequired, NumberRange, Length


class FeedbackForm(FlaskForm):
    event_id = HiddenField("Event ID", validators=[DataRequired()])
    rating = IntegerField(
        "Rating (1-5)",
        validators=[
            DataRequired(),
            NumberRange(
                min=1, max=5, message="Rating must be between 1 and 5"),
        ],
    )
    comments = TextAreaField(
        "Comments", validators=[DataRequired(), Length(max=500)]
    )
    submit = SubmitField("Submit Feedback")
