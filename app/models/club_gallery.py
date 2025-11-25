# File: app/models/club_gallery.py

from app.extensions import db
from datetime import datetime

class ClubGallery(db.Model):
    __tablename__ = 'club_gallery'

    image_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.club_id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    caption = db.Column(db.String(255))

    club = db.relationship("Club", back_populates="gallery_images")
    uploader = db.relationship("User", backref="uploaded_images")
