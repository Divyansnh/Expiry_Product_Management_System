from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_session import Session
import os
from datetime import timedelta

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
scheduler = APScheduler()
cors = CORS()
jwt = JWTManager()
mail = Mail()

def init_extensions(app):
    """Initialize Flask extensions."""
    cors.init_app(app)
    jwt.init_app(app)
    scheduler.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Configure session
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = os.path.join(app.root_path, 'flask_session')
    app.config['SESSION_FILE_THRESHOLD'] = 100
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_NAME'] = 'expiry_tracker_session'
    app.config['SESSION_COOKIE_MAX_AGE'] = 24 * 60 * 60  # 24 hours in seconds
    app.config['SESSION_COOKIE_EXPIRES'] = timedelta(hours=24)
    
    # Initialize session
    Session(app)

    # Initialize database and migrations
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize mail with debug logging
    mail.init_app(app)
    if app.debug:
        print("Mail server configuration:")
        print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
        print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
        print(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
        print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
        print(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")
    
    login_manager.init_app(app) 