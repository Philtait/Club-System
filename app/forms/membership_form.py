# File: app/forms/membership_form.py

from flask_wtf import FlaskForm
from wtforms import IntegerField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Optional

class MembershipForm(FlaskForm):
    student_id = IntegerField('Student ID', validators=[DataRequired()])
    club_id = IntegerField('Club ID', validators=[DataRequired()])
    joined_on = DateTimeField('Joined On', validators=[Optional()], format='%Y-%m-%d %H:%M')
    left_on = DateTimeField('Left On', validators=[Optional()], format='%Y-%m-%d %H:%M')

    submit = SubmitField('Save Membership')
