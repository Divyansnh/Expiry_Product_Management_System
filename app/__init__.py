import logging
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app.core.config import Config
from app.core.extensions import db, login_manager, jwt, migrate, cors, init_extensions, scheduler, mail
from app.core.errors import register_error_handlers
from app.core.middleware import log_request, handle_cors, validate_request
from app.routes import main_bp, auth_bp
from app.routes.reports import reports_bp
from app.api.v1 import api_bp
from app.tasks.cleanup import cleanup_expired_items
import os

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(config_class)
    
    # Initialize extensions
    init_extensions(app)
    
    # Schedule cleanup task to run daily at midnight
    def cleanup_with_context():
        with app.app_context():
            cleanup_expired_items()
    
    scheduler.add_job(
        id='cleanup_expired_items',
        func=cleanup_with_context,
        trigger='cron',
        hour=0,
        minute=0
    )
    
    # Start the scheduler
    scheduler.start()
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register middleware
    log_request(app)
    handle_cors(app)
    validate_request(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(reports_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app 