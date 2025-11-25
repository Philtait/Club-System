# File: app/routes/profile.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.forms import EditProfileForm
from werkzeug.utils import secure_filename
import os

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/", methods=["GET"])
@login_required
def view_profile():
    return render_template("profile.html", user=current_user)


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    # Initialize form with existing data
    form = EditProfileForm(obj=current_user)
    if request.method == "GET":
        # Populate Student/Admin fields
        if current_user.role == "Student" and hasattr(current_user, 'student'):
            student = current_user.student
            form.school.data = student.school
            form.program.data = student.program
            form.year_of_study.data = student.year_of_study
            form.expected_graduation_year.data = student.expected_graduation_year
            form.interests.data = student.interests
        elif current_user.role == "Admin" and hasattr(current_user, 'admin'):
            admin = current_user.admin
            form.staff_id.data = admin.staff_id
            form.department_name.data = admin.department_name

    if form.validate_on_submit():
        # Update User fields
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        current_user.gender = form.gender.data

        # Handle profile image upload
        if form.profile_image.data:
            f = form.profile_image.data
            filename = secure_filename(f.filename)
            upload_folder = os.path.join(
                current_app.root_path, 'static', 'images', 'profiles'
            )
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            f.save(filepath)
            current_user.profile_image = f"images/profiles/{filename}"

        # Update Student or Admin-specific data
        if current_user.role == "Student" and hasattr(current_user, 'student'):
            student = current_user.student
            student.school = form.school.data
            student.program = form.program.data
            student.year_of_study = form.year_of_study.data
            student.expected_graduation_year = form.expected_graduation_year.data
            student.interests = form.interests.data
        elif current_user.role == "Admin" and hasattr(current_user, 'admin'):
            admin = current_user.admin
            admin.staff_id = form.staff_id.data
            admin.department_name = form.department_name.data

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile.view_profile"))

    return render_template(
        "edit_profile.html",
        form=form,
        user=current_user
    )
