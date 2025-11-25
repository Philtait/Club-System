# File: app/models/feedback.py

from app.extensions import db
from datetime import datetime


class Feedback(db.Model):
    __tablename__ = "feedback"

    feedback_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
    )
    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.event_id", ondelete="CASCADE"),
        nullable=False,
    )
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(
        db.Integer, nullable=True
    )  # CHECK constraint is handled in the database
    submitted_on = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="feedback")
    event = db.relationship("Event", back_populates="feedback")
