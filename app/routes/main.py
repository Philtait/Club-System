# File: app/routes/main.py

from flask import Blueprint, render_template
from app.models import Club

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Grab the six most recently created clubs to feature on the homepage
    featured_clubs = (
        Club.query
            .filter_by(status='approved')  # Only show approved clubs
            .order_by(Club.created_at.desc())
            .limit(6)
            .all()
    )
    return render_template('index.html', featured_clubs=featured_clubs)
