# This file makes the config directory a Python package 

"""Application configuration."""
import os
from datetime import timedelta

class Config:
    """Base configuration."""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # APScheduler
    SCHEDULER_API_ENABLED = True
    SCHEDULER_RUN = True
    SCHEDULER_JOBS = [
        {
            'id': 'cleanup_unverified_users',
            'func': 'app.tasks.cleanup:cleanup_unverified_users',
            'trigger': 'interval',
            'hours': 1
        },
        {
            'id': 'cleanup_expired_items',
            'func': 'app.tasks.cleanup:cleanup_expired_items',
            'trigger': 'interval',
            'hours': 1
        }
    ]
    
    # Security
    VERIFICATION_CODE_EXPIRY = timedelta(minutes=15)
    PASSWORD_RESET_EXPIRY = timedelta(hours=1)
    
    # Zoho
    ZOHO_CLIENT_ID = os.environ.get('ZOHO_CLIENT_ID')
    ZOHO_CLIENT_SECRET = os.environ.get('ZOHO_CLIENT_SECRET')
    ZOHO_ORGANIZATION_ID = os.environ.get('ZOHO_ORGANIZATION_ID') 