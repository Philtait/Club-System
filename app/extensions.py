# File: app/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_login import LoginManager
from flask_moment import Moment

# Initialize extensions (to be called in app/__init__.py)
db = SQLAlchemy()
csrf = CSRFProtect()
moment = Moment()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
