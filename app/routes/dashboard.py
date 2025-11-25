# File: app/routes/dashboard.py

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.membership import Membership
from app.models.event_registration import EventRegistration
from app.models.feedback import Feedback
from app.models.club import Club
from app.models.event import Event
from app.models.user import User
from app.models.student import Student
from app.models.club_leader import ClubLeader

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def dashboard():
    stats = {}

    # --- Student dashboard ---
    if current_user.role == 'Student' and current_user.student:
        sid = current_user.student.student_id

        # summary stats
        stats['active_memberships'] = Membership.query.filter_by(
            student_id=sid,
            left_on=None,
            status='Approved'
        ).count()
        stats['upcoming_registered'] = EventRegistration.query.join(Event).filter(
            EventRegistration.student_id == sid,
            Event.event_date >= datetime.utcnow()
        ).count()
        stats['past_events'] = EventRegistration.query.join(Event).filter(
            EventRegistration.student_id == sid,
            Event.event_date < datetime.utcnow()
        ).count()
        stats['feedback_count'] = Feedback.query.filter_by(
            student_id=sid
        ).count()

        # lists for “My Clubs” and “Upcoming Events”
        memberships = Membership.query.filter_by(
            student_id=sid,
            left_on=None,
            status='Approved'
        ).all()
        upcoming_events = Event.query.join(EventRegistration).filter(
            EventRegistration.student_id == sid,
            Event.event_date >= datetime.utcnow()
        ).all()

        return render_template(
            'dashboard.html',
            stats=stats,
            memberships=memberships,
            upcoming_events=upcoming_events
        )

    # --- ClubLeader dashboard ---
    elif current_user.role == 'ClubLeader' and current_user.club_leaderships:
        # Gather the clubs this user leads
        club_ids = [cl.club_id for cl in current_user.club_leaderships]

        # 1) Basic stats
        stats['clubs_led'] = len(club_ids)
        stats['pending_requests'] = Membership.query.filter(
            Membership.club_id.in_(club_ids),
            Membership.status == 'Pending'
        ).count()

        # 2) Active members
        members = (
            Membership.query
            .filter(
                Membership.club_id.in_(club_ids),
                Membership.status == 'Approved',
                Membership.left_on.is_(None)
            )
            .options(
                joinedload(Membership.student).joinedload(Student.user),
                joinedload(Membership.club)
            )
            .order_by(Membership.joined_on.desc())
            .all()
        )

        # 3) Upcoming event registrations
        upcoming_regs = (
            EventRegistration.query
            .join(Event)
            .filter(
                Event.club_id.in_(club_ids),
                Event.event_date >= datetime.utcnow()
            )
            .options(
                joinedload(EventRegistration.event),
                joinedload(EventRegistration.student).joinedload(Student.user)
            )
            .order_by(Event.event_date.asc())
            .all()
        )

        # 4) Pending membership requests list
        pending_requests = (
            Membership.query
            .filter(
                Membership.club_id.in_(club_ids),
                Membership.status == 'Pending'
            )
            .options(
                joinedload(Membership.student).joinedload(Student.user)
            )
            .order_by(Membership.joined_on.desc())
            .all()
        )

        # 5) Feedback for your events
        feedbacks = (
            Feedback.query
            .join(Event)
            .filter(Event.club_id.in_(club_ids))
            .options(joinedload(Feedback.event))
            .order_by(Feedback.submitted_on.desc())
            .all()
        )

        return render_template(
            'dashboard.html',
            stats=stats,
            members=members,
            upcoming_regs=upcoming_regs,
            pending_requests=pending_requests,
            feedbacks=feedbacks
        )

    # --- Admin dashboard ---
    elif current_user.role == 'Admin':
        stats['total_users'] = User.query.count()
        stats['total_clubs'] = Club.query.filter_by(status='Approved').count()
        stats['total_events'] = Event.query.count()
        return render_template('dashboard.html', stats=stats)

    # Fallback
    return redirect(url_for('main.index'))