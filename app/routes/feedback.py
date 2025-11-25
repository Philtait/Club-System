# File: app/routes/feedback.py

from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.feedback import Feedback
from app.models.event import Event
from app.forms import FeedbackForm

feedback_bp = Blueprint("feedback", __name__, url_prefix="/feedback")


@feedback_bp.route("/")
@feedback_bp.route("/event/<int:event_id>")
@login_required
def list_feedback(event_id=None):
    """List feedback - either all feedback or for a specific event."""
    if current_user.role != "Student" or not current_user.student:
        return redirect(url_for("dashboard.dashboard"))

    sid = current_user.student.student_id
    query = Feedback.query.filter_by(student_id=sid)

    if event_id:
        event = Event.query.get_or_404(event_id)
        query = query.filter_by(event_id=event_id)
        items = query.order_by(Feedback.submitted_on.desc()).all()
        return render_template(
            "feedback/view_feedback.html",
            feedbacks=items,
            event=event,  # Pass the specific event
        )
    else:
        # For general feedback list, eager load events
        items = (
            query.options(joinedload(Feedback.event))
            .order_by(Feedback.submitted_on.desc())
            .all()
        )
        return render_template("feedback/list_feedback.html", feedbacks=items)


@feedback_bp.route("/new/<int:event_id>", methods=["GET", "POST"])
@login_required
def new_feedback(event_id):
    """Submit new feedback for a specific event."""
    if current_user.role != "Student" or not current_user.student:
        return redirect(url_for("dashboard.dashboard"))

    event = Event.query.get_or_404(event_id)
    form = FeedbackForm()
    form.event_id.data = event_id  # Pre-populate the event ID

    if form.validate_on_submit():
        fb = Feedback(
            student_id=current_user.student.student_id,
            event_id=event_id,
            rating=form.rating.data,
            message=form.comments.data,  # Use 'message' field from model
            submitted_on=datetime.utcnow(),
        )
        db.session.add(fb)
        db.session.commit()
        flash("Feedback submitted. Thank you!", "success")
        return redirect(url_for("feedback.list_feedback", event_id=event_id))

    return render_template(
        "feedback/submit_feedback.html", form=form, event=event
    )


@feedback_bp.route("/<int:fb_id>/delete", methods=["POST"])
@login_required
def delete_feedback(fb_id):
    """Allow a student to delete their own feedback."""
    fb = Feedback.query.get_or_404(fb_id)
    if (
        current_user.role != "Student"
        or not current_user.student
        or fb.student_id != current_user.student.student_id
    ):
        abort(403)
    db.session.delete(fb)
    db.session.commit()
    flash("Feedback deleted.", "info")
    return redirect(url_for("feedback.list_feedback"))


@feedback_bp.route("/event")
@login_required
def event_feedback():
    """
    ClubLeader view: list all feedback for events
    in the clubs they lead.
    """
    if current_user.role != "ClubLeader":
        abort(403)

    # Gather club IDs this leader manages
    club_ids = [cl.club_id for cl in current_user.club_leaderships]

    # Query Feedback joined to Event, filtered by those club IDs
    feedbacks = (
        Feedback.query.join(Event)
        .filter(Event.club_id.in_(club_ids))
        .options(joinedload(Feedback.event))
        .order_by(Feedback.submitted_on.desc())
        .all()
    )

    return render_template("feedback/event_feedback.html", feedbacks=feedbacks)


@feedback_bp.route("/submit/<int:event_id>", methods=["GET", "POST"])
@login_required
def submit_feedback(event_id):
    """Handle feedback submission for a specific event."""
    if current_user.role != "Student" or not current_user.student:
        return redirect(url_for("dashboard.dashboard"))

    event = Event.query.get_or_404(event_id)
    form = FeedbackForm()

    # Check if feedback already exists
    existing_feedback = Feedback.query.filter_by(
        student_id=current_user.student.student_id, event_id=event_id
    ).first()

    if form.validate_on_submit():
        if existing_feedback:
            # Update existing feedback
            existing_feedback.rating = form.rating.data
            existing_feedback.message = (
                form.comments.data
            )  # Use 'message' field from model
            flash("Feedback updated successfully!", "success")
        else:
            # Create new feedback
            fb = Feedback(
                student_id=current_user.student.student_id,
                event_id=event_id,
                rating=form.rating.data,
                message=form.comments.data,  # Use 'message' field from model
                submitted_on=datetime.utcnow(),
            )
            db.session.add(fb)
            flash("Feedback submitted. Thank you!", "success")

        db.session.commit()
        return redirect(url_for("events.view_event", event_id=event_id))

    # Pre-populate form if feedback exists
    if existing_feedback and not form.is_submitted():
        form.rating.data = existing_feedback.rating
        form.comments.data = (
            existing_feedback.message
        )  # Use 'message' field from model

    return render_template(
        "feedback/submit_feedback.html", form=form, event=event
    )


@feedback_bp.route("/view/<int:event_id>")
@login_required
def view_event_feedback(event_id):
    """View feedback for a specific event."""
    if current_user.role != "Student" or not current_user.student:
        return redirect(url_for("dashboard.dashboard"))

    event = Event.query.get_or_404(event_id)
    feedback = Feedback.query.filter_by(
        student_id=current_user.student.student_id, event_id=event_id
    ).first()

    return render_template(
        "feedback/view_feedback.html",
        event=event,
        feedback=feedback,  # Pass single feedback or None
    )
