# File: app/forms/event_form.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField
from wtforms.fields import DateTimeLocalField, DateField
from wtforms.validators import DataRequired, Optional, Length
from flask_wtf.file import FileField, FileAllowed


class EventForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Description", validators=[DataRequired()])
    location = StringField(
        "Location", validators=[DataRequired(), Length(max=255)]
    )
    event_date = DateTimeLocalField(
        "Event Date", validators=[DataRequired()], format="%Y-%m-%dT%H:%M"
    )
    registration_deadline = DateField(
        "Registration Deadline", validators=[Optional()]
    )
    max_attendees = IntegerField("Maximum Attendees", validators=[Optional()])
    image_url = FileField(
        "Event Image",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png"], "Images only!"),
        ],
    )

    submit = SubmitField("Create Event")
