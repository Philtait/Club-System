# File: app/models/event.py

from app.extensions import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = 'events'

    event_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.club_id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    image_url = db.Column(db.String(255))
    registration_deadline = db.Column(db.Date)
    max_attendees = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    club = db.relationship("Club", back_populates="events")
    registrations = db.relationship("EventRegistration", back_populates="event", cascade="all, delete")
    feedback = db.relationship("Feedback", back_populates="event", cascade="all, delete")
