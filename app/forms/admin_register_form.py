# File: app/forms/admin_register_form.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class AdminRegisterForm(FlaskForm):
    # From users table
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    phone = StringField('Phone', validators=[Length(max=20)])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    role = SelectField('Role', choices=[('Admin', 'Admin')], default='Admin', render_kw={'readonly': True})  # locked

    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    # From admins table
    staff_id = StringField('Staff ID', validators=[DataRequired(), Length(max=30)])
    department_name = StringField('Department', validators=[Length(max=100)])

    submit = SubmitField('Register')
