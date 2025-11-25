# File: app/models/club.py

from datetime import datetime
from app.extensions import db

class Club(db.Model):
    __tablename__ = 'clubs'

    club_id           = db.Column(db.Integer, primary_key=True)
    name              = db.Column(db.String(100), unique=True, nullable=False)
    category          = db.Column(db.String(50), nullable=False)
    objectives        = db.Column(db.Text, nullable=False)
    description       = db.Column(db.Text)
    vision_statement  = db.Column(db.Text)
    past_milestones   = db.Column(db.Text)
    logo_url          = db.Column(db.String(255), default='default-club.jpg')
    banner_url        = db.Column(db.String(255), default='default-banner.jpg')
    meeting_schedule  = db.Column(db.String(100))
    location          = db.Column(db.String(255))
    social_media_handles = db.Column(db.JSON)
    patron_admin_id   = db.Column(db.Integer, db.ForeignKey('admins.admin_id'))
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    patron_admin   = db.relationship(
        "Admin",
        back_populates="clubs"
    )
    club_leaders   = db.relationship(
        "ClubLeader",
        back_populates="club",
        cascade="all, delete-orphan"
    )
    memberships    = db.relationship(
        "Membership",
        back_populates="club",
        cascade="all, delete-orphan"
    )
    events         = db.relationship(
        "Event",
        back_populates="club",
        cascade="all, delete-orphan"
    )
    gallery_images = db.relationship(
        "ClubGallery",
        back_populates="club",
        cascade="all, delete-orphan"
    )
    status         = db.Column(db.String(20), default='pending') 
    def __repr__(self):
        return f"<Club {self.name!r} (id={self.club_id})>"
