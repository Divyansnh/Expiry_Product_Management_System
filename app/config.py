import os
from datetime import timedelta

class Config:
    """Base configuration."""
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    
    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://localhost/expiry_tracker'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
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
    
    # Other configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # APScheduler config
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "UTC"
    
    # JWT config
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-123'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30) 