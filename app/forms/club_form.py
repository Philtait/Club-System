# File: app/forms/club_form.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class ClubForm(FlaskForm):
    name = StringField('Club Name', validators=[DataRequired(), Length(max=100)])
    category = StringField('Category', validators=[DataRequired(), Length(max=50)])
    objectives = TextAreaField('Objectives', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    vision_statement = TextAreaField('Vision Statement', validators=[Optional()])
    past_milestones = TextAreaField('Past Milestones', validators=[Optional()])
    meeting_schedule = StringField('Meeting Schedule', validators=[Optional(), Length(max=100)])
    location = StringField('Location', validators=[Optional(), Length(max=255)])
    social_media_handles = StringField('Social Media Handles (as JSON)', validators=[Optional()])  

    submit = SubmitField('Submit')
