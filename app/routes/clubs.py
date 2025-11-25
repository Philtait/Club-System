# File: app/routes/clubs.py

import os
from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import (
    Club,
    ClubLeader,
    ClubGallery,
    Membership,
    Admin,
    User,
    Student,
)
from app.forms import (
    CreateClubForm,
    MembershipForm,
    ClubGalleryForm,
    AssignLeaderForm,
)
from app.utils.notifications import send_notification

clubs_bp = Blueprint("clubs", __name__, url_prefix="/clubs")


@clubs_bp.route("/")
@login_required
def list_clubs():
    clubs = (
        Club.query.filter_by(status="approved")
        .order_by(Club.created_at.desc())
        .all()
    )
    categories = sorted({c.category for c in clubs})
    return render_template(
        "clubs/list.html", clubs=clubs, categories=categories
    )


@clubs_bp.route("/<int:club_id>")
@login_required
def view_club(club_id):
    club = Club.query.get_or_404(club_id)
    leaders = ClubLeader.query.filter_by(club_id=club_id).all()
    gallery = ClubGallery.query.filter_by(club_id=club_id).all()

    # membership form & state
    membership_form = MembershipForm()
    is_member = False
    is_pending = False

    if current_user.role == "Student" and current_user.student:
        m = Membership.query.filter_by(
            student_id=current_user.student.student_id, club_id=club_id
        ).first()

        if m:
            if m.status == "Approved" and m.left_on is None:
                is_member = True
            elif m.status == "Pending":
                is_pending = True

    # gallery upload form
    gallery_form = ClubGalleryForm()

    return render_template(
        "clubs/view.html",
        club=club,
        leaders=leaders,
        gallery=gallery,
        membership_form=membership_form,
        is_member=is_member,
        is_pending=is_pending,
        gallery_form=gallery_form,
    )


@clubs_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_club():
    if current_user.role != "Admin":
        flash("Only admins can create new clubs.", "danger")
        return redirect(url_for("clubs.list_clubs"))

    form = CreateClubForm()
    if form.validate_on_submit():
        club = Club(
            name=form.name.data,
            category=form.category.data,
            objectives=form.objectives.data,
            description=form.description.data,
            vision_statement=form.vision_statement.data,
            past_milestones=form.past_milestones.data,
            meeting_schedule=form.meeting_schedule.data,
            location=form.location.data,
            social_media_handles={
                k: v
                for k, v in {
                    "instagram": form.instagram.data,
                    "twitter": form.twitter.data,
                }.items()
                if v
            },
            created_at=datetime.utcnow(),
            status="approved",  # Admin-created clubs are auto-approved
        )

        # Set the current admin as patron
        if current_user.admin:
            club.patron_admin_id = current_user.admin.admin_id

        db.session.add(club)
        db.session.flush()

        # optional logo upload
        if form.logo_file.data:
            f = form.logo_file.data
            filename = secure_filename(f.filename)
            folder = os.path.join(
                current_app.root_path,
                "static",
                "images",
                "clubs",
                str(club.club_id),
            )
            os.makedirs(folder, exist_ok=True)
            f.save(os.path.join(folder, filename))
            club.logo_url = f"images/clubs/{club.club_id}/{filename}"
        else:
            club.logo_url = "default-club.jpg"

        db.session.commit()

        # notify admins
        admin_ids = [a.user_id for a in Admin.query.all()]
        title = "New Club Created"
        msg = f"The club '{club.name}' has been created and approved."
        send_notification(title, msg, "Club", club.club_id, admin_ids)

        flash("Club created successfully!", "success")
        return redirect(url_for("clubs.list_clubs"))

    return render_template("clubs/create.html", form=form)


@clubs_bp.route("/request", methods=["GET", "POST"])
@login_required
def request_club():
    if current_user.role not in ("Student", "ClubLeader"):
        flash("Only students or club leaders can request new clubs.", "warning")
        return redirect(url_for("clubs.list_clubs"))

    form = CreateClubForm()
    if form.validate_on_submit():
        club = Club(
            name=form.name.data,
            category=form.category.data,
            objectives=form.objectives.data,
            description=form.description.data,
            vision_statement=form.vision_statement.data,
            past_milestones=form.past_milestones.data,
            meeting_schedule=form.meeting_schedule.data,
            location=form.location.data,
            social_media_handles={
                k: v
                for k, v in {
                    "instagram": form.instagram.data,
                    "twitter": form.twitter.data,
                }.items()
                if v
            },
            created_at=datetime.utcnow(),
            status="pending",  # Requested clubs need approval
            patron_admin_id=None,
        )
        db.session.add(club)
        db.session.flush()

        # optional logo upload
        if form.logo_file.data:
            f = form.logo_file.data
            filename = secure_filename(f.filename)
            folder = os.path.join(
                current_app.root_path,
                "static",
                "images",
                "clubs",
                str(club.club_id),
            )
            os.makedirs(folder, exist_ok=True)
            f.save(os.path.join(folder, filename))
            club.logo_url = f"images/clubs/{club.club_id}/{filename}"
        else:
            club.logo_url = "default-club.jpg"

        db.session.commit()

        # Notify all admins about the new club request
        admin_ids = [a.user_id for a in Admin.query.all()]
        if admin_ids:
            title = "New Club Request"
            msg = f"A new club '{club.name}' has been requested by {current_user.first_name} {current_user.last_name}."
            send_notification(title, msg, "Club", club.club_id, admin_ids)

        flash("Your club request has been submitted for approval.", "info")
        return redirect(url_for("clubs.list_clubs"))

    return render_template("clubs/request_club.html", form=form)


@clubs_bp.route("/pending")
@login_required
def pending_clubs():
    if current_user.role != "Admin":
        flash("Only admins can view pending requests.", "warning")
        return redirect(url_for("dashboard.dashboard"))

    pending = (
        Club.query.filter_by(status="pending")
        .order_by(Club.created_at.desc())
        .all()
    )
    return render_template("clubs/pending_clubs.html", clubs=pending)


@clubs_bp.route("/approve/<int:club_id>")
@login_required
def approve_club(club_id):
    if current_user.role != "Admin":
        flash("Only admins can approve clubs.", "warning")
        return redirect(url_for("dashboard.dashboard"))

    club = Club.query.get_or_404(club_id)
    admin = Admin.query.filter_by(user_id=current_user.user_id).first()
    club.patron_admin_id = admin.admin_id
    club.status = "approved"
    db.session.commit()

    flash(f"Club '{club.name}' approved.", "success")
    return redirect(url_for("clubs.pending_clubs"))


@clubs_bp.route("/<int:club_id>/gallery", methods=["POST"])
@login_required
def upload_gallery(club_id):
    club = Club.query.get_or_404(club_id)
    is_leader = any(
        lead.user_id == current_user.user_id for lead in club.club_leaders
    )
    if current_user.role != "Admin" and not is_leader:
        flash("You don't have permission to add gallery images.", "warning")
        return redirect(url_for("clubs.view_club", club_id=club_id))

    form = ClubGalleryForm()
    if form.validate_on_submit() and form.image_file.data:
        f = form.image_file.data
        filename = secure_filename(f.filename)
        folder = os.path.join(
            current_app.root_path,
            "static",
            "images",
            "clubs",
            str(club_id),
            "gallery",
        )
        os.makedirs(folder, exist_ok=True)
        f.save(os.path.join(folder, filename))
        rel_path = f"images/clubs/{club_id}/gallery/{filename}"

        gallery = ClubGallery(
            club_id=club_id,
            image_url=rel_path,
            uploaded_by=current_user.user_id,
            caption=form.caption.data or None,
        )
        db.session.add(gallery)
        db.session.commit()
        flash("Image added to the gallery!", "success")
    else:
        flash("Please select an image to upload.", "danger")

    return redirect(url_for("clubs.view_club", club_id=club_id))


@clubs_bp.route("/<int:club_id>/leaders", methods=["GET", "POST"])
@login_required
def manage_leaders(club_id):
    """View & assign club leaders (Admin only)."""
    if current_user.role != "Admin":
        flash("Only admins can manage club leaders.", "warning")
        return redirect(url_for("clubs.view_club", club_id=club_id))

    club = Club.query.get_or_404(club_id)
    form = AssignLeaderForm()

    # Build list of existing leader user_ids
    existing = {ldr.user_id for ldr in club.club_leaders}

    # Join User → Student → Membership to find active members who are not yet leaders
    candidates = (
        db.session.query(User)
        .join(Student, Student.user_id == User.user_id)
        .join(Membership, Membership.student_id == Student.student_id)
        .filter(
            Membership.club_id == club_id,
            Membership.status == "Approved",
            Membership.left_on.is_(None),
            ~User.user_id.in_(existing),
        )
        .all()
    )
    form.user_id.choices = [
        (u.user_id, f"{u.first_name} {u.last_name}") for u in candidates
    ]

    if form.validate_on_submit():
        # Check if position is already taken
        existing_position = ClubLeader.query.filter_by(
            club_id=club_id, position=form.position.data
        ).first()

        if existing_position:
            flash(
                f"The position '{form.position.data}' is already assigned.",
                "warning",
            )
            return redirect(url_for("clubs.manage_leaders", club_id=club_id))

        new_leader = ClubLeader(
            user_id=form.user_id.data,
            club_id=club_id,
            position=form.position.data,
        )
        db.session.add(new_leader)

        u = User.query.get(form.user_id.data)
        if u.role != "ClubLeader":
            u.role = "ClubLeader"
            db.session.add(u)
        db.session.commit()
        flash("Leader assigned!", "success")
        return redirect(url_for("clubs.manage_leaders", club_id=club_id))

    leaders = ClubLeader.query.filter_by(club_id=club_id).all()
    return render_template(
        "clubs/manage_leaders.html", club=club, leaders=leaders, form=form
    )


@clubs_bp.route("/<int:club_id>/leaders/remove/<int:leader_id>")
@login_required
def remove_leader(club_id, leader_id):
    """
    Remove a leader from a club (Admin only).
    Demote the user back to 'Student' if they lead no other clubs.
    """
    # Only admins may remove leaders
    if current_user.role != "Admin":
        flash("Only admins can remove leaders.", "warning")
        return redirect(url_for("clubs.view_club", club_id=club_id))

    # Fetch and delete the ClubLeader record
    leader = ClubLeader.query.get_or_404(leader_id)
    user_id = leader.user_id
    db.session.delete(leader)
    db.session.commit()

    # If the user now leads zero clubs, demote them
    remaining = ClubLeader.query.filter_by(user_id=user_id).count()
    if remaining == 0:
        user = User.query.get(user_id)
        user.role = "Student"
        db.session.add(user)
        db.session.commit()

    flash("Leader removed.", "info")
    return redirect(url_for("clubs.manage_leaders", club_id=club_id))


@clubs_bp.route("/<int:club_id>/payment")
@login_required
def club_payment_page(club_id):
    """Redirect to club membership payment page."""
    # Check if user is a student
    if current_user.role != "Student":
        flash("Only students can make membership payments.", "warning")
        return redirect(url_for("clubs.view_club", club_id=club_id))

    if not current_user.student:
        flash("Student profile not found. Please contact support.", "error")
        return redirect(url_for("clubs.view_club", club_id=club_id))

    # Check if user is already a member
    from app.models import Membership

    membership = Membership.query.filter_by(
        student_id=current_user.student.student_id,
        club_id=club_id,
        status="Approved",
        left_on=None,
    ).first()

    if not membership:
        flash(
            "You must be an approved member to make payments for this club.",
            "warning",
        )
        return redirect(url_for("clubs.view_club", club_id=club_id))

    # Redirect to payments blueprint
    return redirect(url_for("payments.membership_payment"))
