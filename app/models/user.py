# File: app/models/user.py

from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    gender = db.Column(db.Enum('Male', 'Female', 'Other'), nullable=False)
    role = db.Column(db.Enum('Student', 'ClubLeader', 'Admin'), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255), default='default-profile.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    student = db.relationship(
        "Student",
        back_populates="user",
        uselist=False,
        cascade="all, delete"
    )
    admin = db.relationship(
        "Admin",
        back_populates="user",
        uselist=False,
        cascade="all, delete"
    )
    club_leaderships = db.relationship(
        "ClubLeader",
        back_populates="user",
        cascade="all, delete"
    )

    # Notifications relationship
    user_notifications = db.relationship(
        "UserNotification",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.user_id)
