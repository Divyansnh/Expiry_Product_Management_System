import logging
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app.config import config
from app.core.extensions import db, login_manager, jwt, migrate, cors, init_extensions, scheduler, mail
from app.core.errors import register_error_handlers
from app.core.middleware import log_request, handle_cors, validate_request
from app.routes import main_bp, auth_bp
from app.routes.reports import reports_bp
from app.api.v1 import api_bp
from app.tasks.cleanup import cleanup_expired_items, cleanup_unverified_accounts
import os

def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Determine which configuration to use
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Load config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    # Only initialize scheduler if not in testing mode
    if not app.config.get('TESTING', False):
        # Define context functions for cleanup tasks
        def cleanup_expired_with_context():
            with app.app_context():
                cleanup_expired_items()
                
        def cleanup_unverified_with_context():
            with app.app_context():
                cleanup_unverified_accounts()
        
        # Add scheduled jobs only if not in testing mode
        with app.app_context():
            # Remove any existing jobs to prevent duplicates
            for job in scheduler.get_jobs():
                scheduler.remove_job(job.id)
            
            # Add new jobs with unique IDs
            if not scheduler.get_job('cleanup_expired_items'):
                scheduler.add_job(
                    id='cleanup_expired_items',
                    func=cleanup_expired_with_context,
                    trigger='cron',
                    hour=0,  # 12 AM (midnight) BST
                    minute=0,
                    timezone='Europe/London',
                    misfire_grace_time=3600  # Allow job to run up to 1 hour late
                )
            
            if not scheduler.get_job('cleanup_unverified_accounts'):
                scheduler.add_job(
                    id='cleanup_unverified_accounts',
                    func=cleanup_unverified_with_context,
                    trigger='cron',
                    hour=0,  # 12 AM (midnight) BST
                    minute=0,
                    timezone='Europe/London',
                    misfire_grace_time=3600  # Allow job to run up to 1 hour late
                )
            
            # Start the scheduler
            if not scheduler.running:
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