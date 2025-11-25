# File: app/routes/membership.py

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    request,
)
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.membership import Membership
from app.models.club_leader import ClubLeader
from app.models.club import Club
from app.models.notification import Notification, UserNotification
from app.models.student import Student
from app.utils.email import (
    send_membership_request_email,
    send_membership_approved_email,
    send_membership_rejected_email,
)

membership_bp = Blueprint("membership", __name__, url_prefix="/membership")


@membership_bp.route("/join/<int:club_id>", methods=["POST"])
@login_required
def join_club(club_id):
    # Only students can request membership
    if current_user.role != "Student":
        flash("Only students can request to join clubs.", "warning")
        return redirect(url_for("clubs.view_club", club_id=club_id))

    # If we reach here and student is still None, there's a data integrity issue
    if current_user.student is None:
        flash("Profile setup incomplete. Please contact support.", "error")
        return redirect(url_for("clubs.view_club", club_id=club_id))

    student_id = current_user.student.student_id

    # Check for any existing membership record
    existing = Membership.query.filter_by(
        student_id=student_id, club_id=club_id
    ).first()

    if existing:
        if existing.status == "Pending":
            flash(
                "Your membership request is already pending approval.", "info"
            )
        elif existing.status == "Approved":
            flash("You are already a member of this club.", "info")
        else:  # Rejected
            existing.status = "Pending"
            existing.joined_on = datetime.utcnow()
            existing.left_on = None
            db.session.commit()
            flash(
                "Your request has been resubmitted and is pending approval.",
                "success",
            )
        return redirect(url_for("clubs.view_club", club_id=club_id))

    # Create a new membership request
    membership = Membership(
        student_id=student_id,
        club_id=club_id,
        status="Pending",
        joined_on=datetime.utcnow(),
    )
    db.session.add(membership)
    db.session.commit()
    flash("Membership request sent. Awaiting approval.", "success")

    # Notify all club leaders via DB notifications and email
    club = Club.query.get_or_404(club_id)
    leaders = ClubLeader.query.filter_by(club_id=club_id).all()
    if leaders:
        # DB notifications
        notif = Notification(
            title="New Membership Request",
            message=(
                f"{current_user.student.user.first_name} "
                f"{current_user.student.user.last_name} "
                f"has requested to join {club.name}"
            ),
            notification_type="Club",
            related_id=membership.membership_id,
            via_email=True,
        )
        db.session.add(notif)
        db.session.flush()  # populate notif.notification_id

        for lead in leaders:
            un = UserNotification(
                user_id=lead.user_id, notification_id=notif.notification_id
            )
            db.session.add(un)
        db.session.commit()

        # Email notifications
        try:
            recipient_emails = [lead.user.email for lead in leaders]
            send_membership_request_email(
                current_user.student.user, club, recipient_emails
            )
        except Exception:
            pass  # Silently fail if email service is not configured

    return redirect(url_for("clubs.view_club", club_id=club_id))


@membership_bp.route("/leave/<int:club_id>", methods=["POST"])
@login_required
def leave_club(club_id):
    # Only students can leave
    if current_user.role != "Student":
        flash("Only students can leave clubs.", "warning")
        return redirect(url_for("clubs.view_club", club_id=club_id))

    student_id = current_user.student.student_id
    membership = Membership.query.filter_by(
        student_id=student_id, club_id=club_id, status="Approved", left_on=None
    ).first()

    if membership:
        membership.left_on = datetime.utcnow()
        db.session.commit()
        flash("You have left the club.", "success")
    else:
        flash("You are not currently an active member.", "info")

    return redirect(url_for("clubs.view_club", club_id=club_id))


@membership_bp.route("/requests/<int:club_id>")
@login_required
def membership_requests(club_id):
    # Only ClubLeaders of this club can view
    is_leader = ClubLeader.query.filter_by(
        club_id=club_id, user_id=current_user.user_id
    ).first()
    if not is_leader:
        abort(403)

    # Fetch only Pending requests, eager-loading student → user
    pending = (
        Membership.query.filter_by(club_id=club_id, status="Pending")
        .options(joinedload(Membership.student).joinedload(Student.user))
        .order_by(Membership.joined_on.desc())
        .all()
    )

    club = Club.query.get_or_404(club_id)
    return render_template(
        "clubs/membership_requests.html", club=club, memberships=pending
    )


@membership_bp.route(
    "/requests/<int:club_id>/approve/<int:mid>", methods=["POST"]
)
@login_required
def approve_member(club_id, mid):
    # Guard: only leaders
    is_leader = ClubLeader.query.filter_by(
        club_id=club_id, user_id=current_user.user_id
    ).first()
    if not is_leader:
        abort(403)

    m = Membership.query.get_or_404(mid)
    if m.club_id != club_id:
        abort(404)

    m.status = "Approved"
    m.joined_on = datetime.utcnow()
    db.session.commit()

    # DB notification for the student
    club = Club.query.get_or_404(club_id)
    notif = Notification(
        title="Membership Approved",
        message=(
            f"Hi {m.student.user.first_name}, your membership in '{club.name}' has been approved."
        ),
        notification_type="Club",
        related_id=m.membership_id,
        via_email=False,
    )
    db.session.add(notif)
    db.session.flush()
    user_notif = UserNotification(
        user_id=m.student.user.user_id, notification_id=notif.notification_id
    )
    db.session.add(user_notif)
    db.session.commit()

    # Email notification
    try:
        send_membership_approved_email(m.student.user, club)
    except Exception:
        pass  # Silently fail if email service is not configured

    flash("Member approved and notified.", "success")

    return redirect(request.referrer or f"/membership/requests/{club_id}")


@membership_bp.route(
    "/requests/<int:club_id>/reject/<int:mid>", methods=["POST"]
)
@login_required
def reject_member(club_id, mid):
    # Guard: only leaders
    is_leader = ClubLeader.query.filter_by(
        club_id=club_id, user_id=current_user.user_id
    ).first()
    if not is_leader:
        abort(403)

    m = Membership.query.get_or_404(mid)
    if m.club_id != club_id:
        abort(404)

    m.status = "Rejected"
    db.session.commit()

    # DB notification for the student
    club = Club.query.get_or_404(club_id)
    notif = Notification(
        title="Membership Rejected",
        message=(
            f"Hi {m.student.user.first_name}, your membership request for '{club.name}' was rejected."
        ),
        notification_type="Club",
        related_id=m.membership_id,
        via_email=False,
    )
    db.session.add(notif)
    db.session.flush()
    user_notif = UserNotification(
        user_id=m.student.user.user_id, notification_id=notif.notification_id
    )
    db.session.add(user_notif)
    db.session.commit()

    # Email notification
    try:
        send_membership_rejected_email(m.student.user, club)
    except Exception:
        pass  # Silently fail if email service is not configured

    flash("Membership request rejected and student notified.", "info")

    return redirect(request.referrer or f"/membership/requests/{club_id}")


# File: app/routes/membership.py (Add these routes to your existing file)

# Add these imports to your existing imports
from functools import wraps


# Add this decorator after your existing imports
def club_leader_or_admin_required(f):
    """Decorator to ensure user is a club leader for the specific club or admin."""

    @wraps(f)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))

        # Get club_id from kwargs or request
        club_id = kwargs.get("club_id") or request.view_args.get("club_id")

        if current_user.role == "Admin":
            return f(*args, **kwargs)
        elif current_user.role == "ClubLeader":
            # Check if user is a leader of this specific club
            is_leader = ClubLeader.query.filter_by(
                club_id=club_id, user_id=current_user.user_id
            ).first()
            if is_leader:
                return f(*args, **kwargs)

        flash("Access denied. Club leaders and admins only.", "danger")
        return redirect(url_for("clubs.view_club", club_id=club_id))

    return decorated_view


@membership_bp.route("/club/<int:club_id>/members")
@login_required
@club_leader_or_admin_required
def club_members(club_id):
    """View all members of a specific club with management capabilities."""
    club = Club.query.get_or_404(club_id)

    # Get all memberships for this club, organized by status
    all_memberships = (
        Membership.query.filter_by(club_id=club_id)
        .options(joinedload(Membership.student).joinedload(Student.user))
        .order_by(Membership.joined_on.desc())
        .all()
    )

    # Separate by status
    pending_members = [m for m in all_memberships if m.status == "Pending"]
    approved_members = [
        m
        for m in all_memberships
        if m.status == "Approved" and m.left_on is None
    ]
    rejected_members = [m for m in all_memberships if m.status == "Rejected"]
    former_members = [m for m in all_memberships if m.left_on is not None]

    return render_template(
        "membership/club_members.html",
        club=club,
        pending_members=pending_members,
        approved_members=approved_members,
        rejected_members=rejected_members,
        former_members=former_members,
    )


@membership_bp.route("/remove/<int:membership_id>", methods=["POST"])
@login_required
def remove_member(membership_id):
    """Remove an approved member from the club."""
    membership = Membership.query.get_or_404(membership_id)
    club = membership.club

    # Check permissions
    if current_user.role == "ClubLeader":
        is_leader = ClubLeader.query.filter_by(
            club_id=club.club_id, user_id=current_user.user_id
        ).first()
        if not is_leader:
            flash(
                "You can only manage memberships for clubs where you are a leader.",
                "danger",
            )
            return redirect(url_for("clubs.view_club", club_id=club.club_id))
    elif current_user.role != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("clubs.view_club", club_id=club.club_id))

    if membership.status != "Approved":
        flash("This person is not an active member.", "warning")
        return redirect(
            url_for("membership.club_members", club_id=club.club_id)
        )

    # Get removal reason from form
    reason = request.form.get("reason", "Removed by club leadership")

    # Remove the member
    membership.left_on = datetime.utcnow()
    membership.status = "Removed"
    db.session.commit()

    # Send notification to student
    notif = Notification(
        title="Club Membership Ended",
        message=f"Your membership in {club.name} has been ended. Reason: {reason}",
        notification_type="Club",
        related_id=membership.membership_id,
        via_email=False,
    )
    db.session.add(notif)
    db.session.flush()

    user_notif = UserNotification(
        user_id=membership.student.user.user_id,
        notification_id=notif.notification_id,
    )
    db.session.add(user_notif)
    db.session.commit()

    flash(
        f"Removed {membership.student.user.first_name} {membership.student.user.last_name} from the club.",
        "info",
    )
    return redirect(url_for("membership.club_members", club_id=club.club_id))


@membership_bp.route("/all-pending")
@login_required
def all_pending_memberships():
    """Admin view of all pending memberships across all clubs."""
    if current_user.role != "Admin":
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    pending_memberships = (
        Membership.query.filter_by(status="Pending")
        .options(
            joinedload(Membership.student).joinedload(Student.user),
            joinedload(Membership.club),
        )
        .order_by(Membership.joined_on.desc())
        .all()
    )

    return render_template(
        "membership/all_pending.html", pending_memberships=pending_memberships
    )


@membership_bp.route("/club/<int:club_id>/statistics")
@login_required
@club_leader_or_admin_required
def club_statistics(club_id):
    """View membership statistics for a club."""
    club = Club.query.get_or_404(club_id)

    # Get membership statistics
    stats = {
        "total_approved": Membership.query.filter_by(
            club_id=club_id, status="Approved"
        )
        .filter(Membership.left_on.is_(None))
        .count(),
        "total_pending": Membership.query.filter_by(
            club_id=club_id, status="Pending"
        ).count(),
        "total_rejected": Membership.query.filter_by(
            club_id=club_id, status="Rejected"
        ).count(),
        "total_left": Membership.query.filter_by(club_id=club_id)
        .filter(Membership.left_on.isnot(None))
        .count(),
        "total_removed": Membership.query.filter_by(
            club_id=club_id, status="Removed"
        ).count(),
    }

    # Get recent activity
    recent_memberships = (
        Membership.query.filter_by(club_id=club_id)
        .options(joinedload(Membership.student).joinedload(Student.user))
        .order_by(Membership.joined_on.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "membership/club_statistics.html",
        club=club,
        stats=stats,
        recent_memberships=recent_memberships,
    )


# Enhanced approve_member route to include reason parameter
@membership_bp.route("/approve/<int:membership_id>", methods=["POST"])
@login_required
def approve_membership(membership_id):
    """Approve a pending membership with enhanced functionality."""
    membership = Membership.query.get_or_404(membership_id)
    club = membership.club

    # Check permissions
    if current_user.role == "ClubLeader":
        is_leader = ClubLeader.query.filter_by(
            club_id=club.club_id, user_id=current_user.user_id
        ).first()
        if not is_leader:
            flash(
                "You can only manage memberships for clubs where you are a leader.",
                "danger",
            )
            return redirect(url_for("clubs.view_club", club_id=club.club_id))
    elif current_user.role != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("clubs.view_club", club_id=club.club_id))

    if membership.status != "Pending":
        flash("This membership request is not pending.", "warning")
        return redirect(
            request.referrer
            or url_for("membership.club_members", club_id=club.club_id)
        )

    # Approve the membership
    membership.status = "Approved"
    membership.joined_on = datetime.utcnow()
    db.session.commit()

    # Send notification (reuse existing notification logic)
    notif = Notification(
        title="Membership Approved",
        message=f"Hi {membership.student.user.first_name}, your membership in '{club.name}' has been approved.",
        notification_type="Club",
        related_id=membership.membership_id,
        via_email=False,
    )
    db.session.add(notif)
    db.session.flush()

    user_notif = UserNotification(
        user_id=membership.student.user.user_id,
        notification_id=notif.notification_id,
    )
    db.session.add(user_notif)
    db.session.commit()

    flash(
        f"Membership approved for {membership.student.user.first_name} {membership.student.user.last_name}.",
        "success",
    )
    return redirect(
        request.referrer
        or url_for("membership.club_members", club_id=club.club_id)
    )


@membership_bp.route("/reject/<int:membership_id>", methods=["POST"])
@login_required
def reject_membership(membership_id):
    """Reject a pending membership with enhanced functionality."""
    membership = Membership.query.get_or_404(membership_id)
    club = membership.club

    # Check permissions
    if current_user.role == "ClubLeader":
        is_leader = ClubLeader.query.filter_by(
            club_id=club.club_id, user_id=current_user.user_id
        ).first()
        if not is_leader:
            flash(
                "You can only manage memberships for clubs where you are a leader.",
                "danger",
            )
            return redirect(url_for("clubs.view_club", club_id=club.club_id))
    elif current_user.role != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("clubs.view_club", club_id=club.club_id))

    if membership.status != "Pending":
        flash("This membership request is not pending.", "warning")
        return redirect(
            request.referrer
            or url_for("membership.club_members", club_id=club.club_id)
        )

    # Get rejection reason from form
    reason = request.form.get("reason", "No reason provided")

    # Reject the membership
    membership.status = "Rejected"
    db.session.commit()

    # Send notification
    notif = Notification(
        title="Membership Request Rejected",
        message=f"Your membership request for {club.name} was not approved. Reason: {reason}",
        notification_type="Club",
        related_id=membership.membership_id,
        via_email=False,
    )
    db.session.add(notif)
    db.session.flush()

    user_notif = UserNotification(
        user_id=membership.student.user.user_id,
        notification_id=notif.notification_id,
    )
    db.session.add(user_notif)
    db.session.commit()

    flash(
        f"Membership rejected for {membership.student.user.first_name} {membership.student.user.last_name}.",
        "info",
    )
    return redirect(
        request.referrer
        or url_for("membership.club_members", club_id=club.club_id)
    )


# API endpoint for member count
@membership_bp.route("/api/club/<int:club_id>/member-count")
@login_required
def api_member_count(club_id):
    """API endpoint to get current member count."""
    count = (
        Membership.query.filter_by(club_id=club_id, status="Approved")
        .filter(Membership.left_on.is_(None))
        .count()
    )

    return {"member_count": count}
