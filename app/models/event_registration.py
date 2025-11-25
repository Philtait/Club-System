# File: app/models/event_registration.py

from app.extensions import db
from datetime import datetime

class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'

    reg_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)
    attended = db.Column(db.Boolean, default=False)

    event = db.relationship("Event", back_populates="registrations")
    student = db.relationship("Student", backref="event_registrations")

    __table_args__ = (
        db.UniqueConstraint('event_id', 'student_id', name='unique_registration'),
    )
