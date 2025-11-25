# File: app/forms/register_form.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegisterForm(FlaskForm):
    # Users table fields
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    phone = StringField('Phone Number', validators=[Length(max=20)])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    role = SelectField('Role', choices=[('Student', 'Student')], default='Student', render_kw={'readonly': True})  # Locked to 'Student'

    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])

    # Students table fields
    school = StringField('School', validators=[Length(max=100)])
    program = StringField('Program', validators=[Length(max=100)])
    year_of_study = IntegerField('Year of Study')
    expected_graduation_year = IntegerField('Expected Graduation Year')
    interests = TextAreaField('Interests')

    submit = SubmitField('Register')
