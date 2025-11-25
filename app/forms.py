# File: app/forms.py (Fresh complete version - no M-PESA, clean implementation)

from wtforms import FileField
from wtforms.validators import Optional
from wtforms.validators import NumberRange
from wtforms.validators import DataRequired, Length
from wtforms import (
    StringField,
    SelectField,
    IntegerField,
    TextAreaField,
)
from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    SubmitField,
    BooleanField,
)
from wtforms.validators import (
    Email,
    EqualTo,
    Regexp,
)
from flask_wtf.file import FileAllowed
from wtforms.widgets import TextArea
from wtforms.fields import DateField, DateTimeLocalField

password_requirements = [
    DataRequired(),
    Length(min=8, message="At least 8 characters required."),
    Regexp(r".*[A-Z].*", message="Must contain at least one uppercase letter."),
    Regexp(r".*[a-z].*", message="Must contain at least one lowercase letter."),
    Regexp(r".*\d.*", message="Must contain at least one digit."),
    Regexp(
        r".*[@$!%*?&].*",
        message="Must contain at least one special character (@$!%*?&).",
    ),
]


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    first_name = StringField(
        "First Name", validators=[DataRequired(), Length(max=50)]
    )
    last_name = StringField(
        "Last Name", validators=[DataRequired(), Length(max=50)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    gender = SelectField(
        "Gender",
        choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
        validators=[DataRequired()],
    )
    role = SelectField(
        "Role",
        choices=[
            ("Student", "Student"),
            ("ClubLeader", "Club Leader"),
            ("Admin", "Admin"),
        ],
        validators=[DataRequired()],
    )

    # Student fields
    school = StringField(
        "School/Faculty", validators=[Optional(), Length(max=100)]
    )
    program = StringField("Program", validators=[Optional(), Length(max=100)])
    year_of_study = IntegerField(
        "Year of Study", validators=[Optional(), NumberRange(min=1)]
    )
    expected_graduation_year = DateField(
        "Expected Graduation Year", validators=[Optional()]
    )
    interests = TextAreaField(
        "Interests", validators=[Optional(), Length(max=500)]
    )

    # Admin fields
    staff_id = StringField("Staff ID", validators=[Optional(), Length(max=30)])
    department_name = StringField(
        "Department", validators=[Optional(), Length(max=100)]
    )

    password = PasswordField("Password", validators=password_requirements)
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )

    submit = SubmitField("Register")


class EditProfileForm(FlaskForm):
    first_name = StringField(
        "First Name", validators=[DataRequired(), Length(max=50)]
    )
    last_name = StringField(
        "Last Name", validators=[DataRequired(), Length(max=50)]
    )
    email = StringField("Email", render_kw={"readonly": True})
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    gender = SelectField(
        "Gender",
        choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
        validators=[Optional()],
    )
    profile_image = FileField("Profile Image", validators=[Optional()])

    # Student fields
    school = StringField("School", validators=[Optional(), Length(max=100)])
    program = StringField("Program", validators=[Optional(), Length(max=100)])
    year_of_study = IntegerField("Year of Study", validators=[Optional()])
    expected_graduation_year = IntegerField(
        "Expected Graduation Year", validators=[Optional()]
    )
    interests = TextAreaField(
        "Interests", validators=[Optional(), Length(max=500)]
    )

    # Admin fields
    staff_id = StringField("Staff ID", validators=[Optional(), Length(max=50)])
    department_name = StringField(
        "Department", validators=[Optional(), Length(max=100)]
    )

    submit = SubmitField("Update Profile")


class CreateClubForm(FlaskForm):
    name = StringField("Club Name", validators=[DataRequired()])
    category = StringField("Category", validators=[DataRequired()])
    objectives = TextAreaField("Objectives", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional()])
    vision_statement = TextAreaField("Vision", validators=[Optional()])
    past_milestones = TextAreaField("Past Milestones", validators=[Optional()])
    meeting_schedule = StringField("Meeting Schedule", validators=[Optional()])
    location = StringField("Location", validators=[Optional()])

    # Individual social media fields
    instagram = StringField(
        "Instagram Handle", validators=[Optional(), Length(max=100)]
    )
    twitter = StringField(
        "Twitter Handle", validators=[Optional(), Length(max=100)]
    )

    # Logo upload
    logo_file = FileField("Club Logo Image", validators=[Optional()])

    submit = SubmitField("Create Club")


class EventForm(FlaskForm):
    club_id = SelectField("Club", coerce=int, validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField(
        "Description", validators=[DataRequired()], widget=TextArea()
    )
    location = StringField(
        "Location", validators=[DataRequired(), Length(max=255)]
    )
    event_date = DateTimeLocalField(
        "Event Date", format="%Y-%m-%dT%H:%M", validators=[DataRequired()]
    )
    registration_deadline = DateField(
        "Registration Deadline", validators=[Optional()]
    )
    max_attendees = IntegerField(
        "Max Attendees", validators=[Optional(), NumberRange(min=1)]
    )
    # Event image upload field
    image_url = FileField(
        "Event Image",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png"], "Images only!"),
        ],
    )
    submit = SubmitField("Create Event")


class MembershipForm(FlaskForm):
    submit = SubmitField("Join Club")


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=password_requirements)
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Reset Password")


class ClubGalleryForm(FlaskForm):
    image_file = FileField("Upload Image", validators=[Optional()])
    caption = StringField("Caption", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Add to Gallery")


class AssignLeaderForm(FlaskForm):
    user_id = SelectField(
        "Select User", coerce=int, validators=[DataRequired()]
    )
    position = SelectField(
        "Position",
        choices=[
            ("President", "President"),
            ("VicePresident", "Vice President"),
            ("Secretary", "Secretary"),
            ("Publicity", "Publicity"),
            ("Finance", "Finance"),
            ("MembershipCoordinator", "Membership Coordinator"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Assign Leader")


class FeedbackForm(FlaskForm):
    rating = IntegerField(
        "Rating (1–5)",
        validators=[
            DataRequired(),
            NumberRange(min=1, max=5, message="Must be between 1 and 5"),
        ],
    )
    comments = TextAreaField(
        "Comments", validators=[DataRequired(), Length(max=500)]
    )
    submit = SubmitField("Submit Feedback")


# Additional forms for specific functionality
class SearchForm(FlaskForm):
    """Form for searching clubs and events."""

    query = StringField(
        "Search",
        validators=[DataRequired(), Length(min=1, max=100)],
        render_kw={"placeholder": "Search clubs, events..."},
    )
    category = SelectField(
        "Category",
        choices=[("", "All Categories")],  # Will be populated dynamically
        validators=[Optional()],
    )
    submit = SubmitField("Search")


class ContactForm(FlaskForm):
    """Form for contacting support or admins."""

    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    subject = StringField(
        "Subject", validators=[DataRequired(), Length(max=200)]
    )
    message = TextAreaField(
        "Message",
        validators=[DataRequired(), Length(max=1000)],
        render_kw={"rows": 5},
    )
    submit = SubmitField("Send Message")


class BulkEmailForm(FlaskForm):
    """Form for admins to send bulk emails."""

    recipients = SelectField(
        "Send To",
        choices=[
            ("all_students", "All Students"),
            ("all_club_leaders", "All Club Leaders"),
            ("specific_club", "Specific Club Members"),
        ],
        validators=[DataRequired()],
    )
    club_id = SelectField("Club", coerce=int, validators=[Optional()])
    subject = StringField(
        "Subject", validators=[DataRequired(), Length(max=200)]
    )
    message = TextAreaField(
        "Message",
        validators=[DataRequired(), Length(max=2000)],
        render_kw={"rows": 8},
    )
    submit = SubmitField("Send Email")


class ClubRequestForm(FlaskForm):
    """Form for requesting new club creation."""

    name = StringField(
        "Proposed Club Name", validators=[DataRequired(), Length(max=100)]
    )
    category = StringField(
        "Category", validators=[DataRequired(), Length(max=50)]
    )
    objectives = TextAreaField(
        "Club Objectives",
        validators=[DataRequired(), Length(max=1000)],
        render_kw={"rows": 5},
    )
    description = TextAreaField(
        "Club Description",
        validators=[DataRequired(), Length(max=1000)],
        render_kw={"rows": 4},
    )
    justification = TextAreaField(
        "Why should this club be approved?",
        validators=[DataRequired(), Length(max=500)],
        render_kw={"rows": 3},
    )
    expected_members = IntegerField(
        "Expected Number of Members",
        validators=[DataRequired(), NumberRange(min=5, max=1000)],
    )
    meeting_schedule = StringField(
        "Proposed Meeting Schedule", validators=[Optional(), Length(max=100)]
    )
    submit = SubmitField("Submit Request")


class EventFilterForm(FlaskForm):
    """Form for filtering events."""

    club = SelectField("Club", coerce=int, validators=[Optional()])
    date_from = DateField("From Date", validators=[Optional()])
    date_to = DateField("To Date", validators=[Optional()])
    location = StringField("Location", validators=[Optional(), Length(max=100)])
    submit = SubmitField("Filter")


class AdminReportForm(FlaskForm):
    """Form for generating admin reports."""

    report_type = SelectField(
        "Report Type",
        choices=[
            ("membership", "Membership Report"),
            ("events", "Events Report"),
            ("payments", "Payments Report"),
            ("activity", "Activity Report"),
        ],
        validators=[DataRequired()],
    )
    date_from = DateField("From Date", validators=[DataRequired()])
    date_to = DateField("To Date", validators=[DataRequired()])
    format = SelectField(
        "Export Format",
        choices=[("html", "HTML"), ("csv", "CSV"), ("pdf", "PDF")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Generate Report")
