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
    SCHEDULER_JOBS = []  # Jobs are now configured in app/__init__.py
    
    # Security
    VERIFICATION_CODE_EXPIRY = timedelta(minutes=15)
    PASSWORD_RESET_EXPIRY = timedelta(hours=1)
    MAX_LOGIN_ATTEMPTS = 5  # Maximum number of failed login attempts before account is locked
    LOGIN_LOCKOUT_DURATION = timedelta(minutes=15)  # How long an account stays locked after too many failed attempts
    
    # Zoho API Configuration
    ZOHO_API_BASE_URL = 'https://www.zohoapis.eu/inventory/v1'
    ZOHO_ACCOUNTS_URL = 'https://accounts.zoho.eu'
    ZOHO_CLIENT_ID = os.environ.get('ZOHO_CLIENT_ID')
    ZOHO_CLIENT_SECRET = os.environ.get('ZOHO_CLIENT_SECRET')
    ZOHO_ORGANIZATION_ID = os.environ.get('ZOHO_ORGANIZATION_ID')
    ZOHO_REDIRECT_URI = os.environ.get('ZOHO_REDIRECT_URI', 'http://localhost:5000/auth/zoho/callback')
    ZOHO_TOKEN_EXPIRY = timedelta(hours=1)

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    
    # Development Zoho settings
    ZOHO_CLIENT_ID = os.environ.get('ZOHO_CLIENT_ID', 'dev-client-id')
    ZOHO_CLIENT_SECRET = os.environ.get('ZOHO_CLIENT_SECRET', 'dev-client-secret')
    ZOHO_REDIRECT_URI = os.environ.get('ZOHO_REDIRECT_URI', 'http://localhost:5000/auth/zoho/callback')
    ZOHO_ORGANIZATION_ID = os.environ.get('ZOHO_ORGANIZATION_ID', 'dev-org-id')

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Production Zoho settings
    ZOHO_CLIENT_ID = os.environ['ZOHO_CLIENT_ID']  # Required in production
    ZOHO_CLIENT_SECRET = os.environ['ZOHO_CLIENT_SECRET']  # Required in production
    ZOHO_REDIRECT_URI = os.environ['ZOHO_REDIRECT_URI']  # Required in production
    ZOHO_ORGANIZATION_ID = os.environ.get('ZOHO_ORGANIZATION_ID', '')

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Testing Zoho settings
    ZOHO_CLIENT_ID = 'test-client-id'
    ZOHO_CLIENT_SECRET = 'test-client-secret'
    ZOHO_REDIRECT_URI = 'http://localhost:5000/auth/zoho/callback'
    ZOHO_ORGANIZATION_ID = 'test-org-id'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 