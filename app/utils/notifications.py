# File: app/utils/notifications.py

from app.extensions import db
from app.models.notification import Notification, UserNotification
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def send_notification(
    title,
    message,
    notification_type,
    related_id=None,
    user_ids=None,
    via_email=True,
):
    """
    Send a notification to multiple users.

    Args:
        title: Notification title
        message: Notification message
        notification_type: Type of notification ('System', 'Club', 'Event')
        related_id: Related object ID (optional)
        user_ids: List of user IDs to send to
        via_email: Whether to also send email notification
    """
    try:
        if not user_ids:
            return False

        # Create the notification
        notification = Notification(
            title=title,
            message=message,
            notification_type=notification_type,
            related_id=related_id,
            via_email=via_email,
            sent_on=datetime.utcnow(),
        )

        db.session.add(notification)
        db.session.flush()  # Get the notification ID

        # Create user notifications
        for user_id in user_ids:
            user_notification = UserNotification(
                user_id=user_id,
                notification_id=notification.notification_id,
                is_read=False,
            )
            db.session.add(user_notification)

        db.session.commit()
        logger.info(f"Notification sent to {len(user_ids)} users: {title}")
        return True

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error sending notification: {e}")
        return False


def mark_notification_read(user_id, notification_id):
    """Mark a specific notification as read for a user."""
    try:
        user_notification = UserNotification.query.filter_by(
            user_id=user_id, notification_id=notification_id
        ).first()

        if user_notification and not user_notification.is_read:
            user_notification.is_read = True
            user_notification.read_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error marking notification as read: {e}")
        return False


def get_unread_count(user_id):
    """Get count of unread notifications for a user."""
    try:
        count = UserNotification.query.filter_by(
            user_id=user_id, is_read=False
        ).count()
        return count
    except Exception as e:
        logger.error(f"Error getting unread count: {e}")
        return 0


def get_user_notifications(user_id, limit=50):
    """Get notifications for a user with pagination."""
    try:
        notifications = (
            db.session.query(UserNotification, Notification)
            .join(
                Notification,
                UserNotification.notification_id
                == Notification.notification_id,
            )
            .filter(UserNotification.user_id == user_id)
            .order_by(Notification.sent_on.desc())
            .limit(limit)
            .all()
        )
        return notifications
    except Exception as e:
        logger.error(f"Error getting user notifications: {e}")
        return []
