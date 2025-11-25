from .auth import auth_bp
from .dashboard import dashboard_bp
from .admin import admin_bp
from .clubs import clubs_bp
from .membership import membership_bp
from .events import events_bp
from .feedback import feedback_bp
from .payments import payments_bp
from .profile import profile_bp
from .notifications import notifications_bp
from .main import main_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(clubs_bp)
    app.register_blueprint(membership_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(main_bp)
