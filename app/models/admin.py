# File: app/models/admin.py

from app.extensions import db

class Admin(db.Model):
    __tablename__ = 'admins'

    admin_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=False)
    staff_id = db.Column(db.String(30), unique=True, nullable=False)
    department_name = db.Column(db.String(100))

    user = db.relationship("User", back_populates="admin")
    clubs = db.relationship("Club", back_populates="patron_admin", cascade="all, delete")
