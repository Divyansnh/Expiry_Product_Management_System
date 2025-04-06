import os
from datetime import timedelta
from typing import Optional

class Config:
    """Base configuration."""
    # Basic Flask config
    SECRET_KEY: str = os.environ['SECRET_KEY']  # Required in all environments
    JWT_SECRET_KEY: str = os.environ['JWT_SECRET_KEY']  # Required in all environments
    
    # Database config
    SQLALCHEMY_DATABASE_URI: str = os.environ['DATABASE_URL']  # Required in all environments
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # Zoho API Configuration
    ZOHO_API_BASE_URL = 'https://inventory.zoho.eu/api/v1'
    ZOHO_ACCOUNTS_URL = 'https://accounts.zoho.eu'
    ZOHO_CLIENT_ID = os.environ.get('ZOHO_CLIENT_ID', '')
    ZOHO_CLIENT_SECRET = os.environ.get('ZOHO_CLIENT_SECRET', '')
    ZOHO_REDIRECT_URI = os.environ.get('ZOHO_REDIRECT_URI', 'http://localhost:5000/auth/zoho/callback')
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = 'app/flask_session'
    SESSION_COOKIE_NAME = 'expiry_tracker_session'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)  # 24 hours
    
    # Security configuration
    PASSWORD_SALT = os.environ['PASSWORD_SALT']  # Required for password hashing
    MAX_LOGIN_ATTEMPTS = 5  # Maximum number of failed login attempts
    LOGIN_LOCKOUT_TIME = timedelta(minutes=15)  # Lockout duration after max attempts
    
    # Other configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # APScheduler config
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "UTC"
    
    # JWT config
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    
    # Override required variables with development defaults
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')  # Only in development
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-key')  # Only in development
    PASSWORD_SALT = os.environ.get('PASSWORD_SALT', 'dev-salt')  # Only in development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://localhost/expiry_tracker_v2')

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Additional production settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Production-specific database settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'max_overflow': 10
    }

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Testing-specific settings
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    PASSWORD_SALT = 'test-salt'
    
    # Disable CSRF protection in testing
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 