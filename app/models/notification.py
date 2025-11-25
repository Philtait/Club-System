# File: app/models/notification.py

from app.extensions import db

class Notification(db.Model):
    __tablename__ = 'notifications'

    notification_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_on = db.Column(db.DateTime, server_default=db.func.now())
    notification_type = db.Column(
        db.Enum('System', 'Club', 'Event', name='notification_type'),
        nullable=False
    )
    related_id = db.Column(db.Integer)
    via_email = db.Column(db.Boolean, default=True)

    # back-reference to UserNotification
    user_notifications = db.relationship(
        'UserNotification',
        back_populates='notification',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Notification {self.title}>"


class UserNotification(db.Model):
    __tablename__ = 'user_notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    notification_id = db.Column(
        db.Integer,
        db.ForeignKey('notifications.notification_id'),
        nullable=False
    )
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)

    # relationships
    user = db.relationship(
        'User',
        back_populates='user_notifications'
    )
    notification = db.relationship(
        'Notification',
        back_populates='user_notifications'
    )

    def __repr__(self):
        status = 'Read' if self.is_read else 'Unread'
        return f"<UserNotification user_id={self.user_id} notif_id={self.notification_id} ({status})>"
