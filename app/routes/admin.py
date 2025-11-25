# File: app/routes/admin.py

from flask import (
    Blueprint, render_template,
    redirect, url_for, flash, request
)
from flask_login import login_required, current_user
from app.extensions import db
from app.models.club import Club
from app.models.admin import Admin


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
@login_required
def require_admin():
    if current_user.role != 'Admin':
        flash("Access denied – Admins only.", "warning")
        return redirect(url_for('dashboard.dashboard'))


@admin_bp.route('/pending_clubs')
def pending_clubs():
    """List all clubs with status='pending'."""
    clubs = (Club.query
                 .filter_by(status='pending')
                 .order_by(Club.created_at.desc())
                 .all())
    return render_template('clubs/pending_clubs.html', clubs=clubs)


@admin_bp.route('/clubs/<int:club_id>/approve', methods=['POST'])
def approve_club(club_id):
    """Mark a club as approved."""
    club = Club.query.get_or_404(club_id)

    # assign this admin as patron and flip status
    admin = Admin.query.filter_by(user_id=current_user.user_id).first()
    club.patron_admin_id = admin.admin_id
    club.status = 'approved'
    db.session.commit()

    flash(f"Club “{club.name}” approved successfully.", "success")
    return redirect(url_for('admin.pending_clubs'))


@admin_bp.route('/clubs/<int:club_id>/reject', methods=['POST'])
def reject_club(club_id):
    """Reject (delete) a pending club."""
    club = Club.query.get_or_404(club_id)
    name = club.name
    db.session.delete(club)
    db.session.commit()
    flash(f"Club “{name}” has been rejected.", "info")
    return redirect(url_for('admin.pending_clubs'))
