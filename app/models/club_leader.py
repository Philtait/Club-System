# File: app/models/club_leader.py

from app.extensions import db
from datetime import datetime

class ClubLeader(db.Model):
    __tablename__ = 'club_leaders'

    leader_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.club_id', ondelete='CASCADE'), nullable=False)
    position = db.Column(db.Enum('President', 'VicePresident', 'Secretary', 'Publicity', 'Finance', 'MembershipCoordinator'), nullable=False)
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="club_leaderships")
    club = db.relationship("Club", back_populates="club_leaders")

    __table_args__ = (
        db.UniqueConstraint('club_id', 'position', name='unique_leader_position'),
    )
