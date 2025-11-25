# File: app/routes/notifications.py

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models.notification import Notification, UserNotification

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@notifications_bp.route("/")
@login_required
def inbox():
    """Show all notifications for the current user."""
    items = (
        db.session.query(UserNotification, Notification)
        .join(Notification, UserNotification.notification_id == Notification.notification_id)
        .filter(UserNotification.user_id == current_user.user_id)
        .order_by(Notification.sent_on.desc())
        .all()
    )
    # items is list of (UserNotification, Notification)
    return render_template("notifications.html", items=items)


@notifications_bp.route("/read/<int:notification_id>")
@login_required
def mark_read(notification_id):
    """Mark a specific notification as read."""
    un = UserNotification.query.filter_by(
        user_id=current_user.user_id,
        notification_id=notification_id
    ).first()
    if un and not un.is_read:
        un.is_read = True
        un.read_at = db.func.now()
        db.session.commit()
    return redirect(url_for("notifications.inbox"))
