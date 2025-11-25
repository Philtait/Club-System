# File: app/__init__.py

import os
import logging
import pymysql
from flask import Flask, render_template
from flask_migrate import Migrate
from itsdangerous import URLSafeTimedSerializer

# Import the one true set of extension objects
from app.extensions import db, login_manager, csrf, mail, moment

# Ensure pymysql is used instead of MySQLdb
pymysql.install_as_MySQLdb()

# Other extensions
migrate = Migrate()
s = URLSafeTimedSerializer(os.environ.get("SECRET_KEY", "default-dev-secret"))

# Flask-Login configuration
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


def create_app():
    app = Flask(__name__)

    # Core configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "mysql://root:12345@localhost/CMS"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Mail configuration
    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = (
        os.environ.get("MAIL_USE_TLS", "True") == "True"
    )
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

    # File upload configuration
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

    # Set up logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    moment.init_app(app)

    # Import models so Flask-Migrate can detect them
    from app import models

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return models.User.query.get(int(user_id))
        except (ValueError, TypeError):
            return None

    # Register all your blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    from app.routes.clubs import clubs_bp
    from app.routes.events import events_bp
    from app.routes.feedback import feedback_bp
    from app.routes.notifications import notifications_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.membership import membership_bp
    from app.routes.payments import payments_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(clubs_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(membership_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(admin_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"Internal server error: {error}")
        return render_template("500.html"), 500

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403

    # Template context processors
    @app.context_processor
    def inject_user():
        from flask_login import current_user

        return dict(current_user=current_user)

    return app
