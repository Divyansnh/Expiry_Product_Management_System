from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.core.extensions import db
from app.models.base import BaseModel
from datetime import datetime, timedelta
import jwt
from flask import current_app
from time import time
import secrets
import string
import re

class User(UserMixin, BaseModel):
    """User model for authentication and user management."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    password_reset_token = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    notification_preferences = db.Column(db.JSON, default=dict)
    
    # Verification fields
    verification_code = db.Column(db.String(6))
    verification_code_expires_at = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Notification preferences
    email_notifications = db.Column(db.Boolean, default=False)
    sms_notifications = db.Column(db.Boolean, default=False)
    in_app_notifications = db.Column(db.Boolean, default=False)
    
    # Relationships
    items = db.relationship('Item', backref='user', lazy=True)
    user_notifications = db.relationship('Notification', backref='notification_user', lazy=True)
    
    # Zoho integration fields
    zoho_client_id = db.Column(db.String(255))
    zoho_client_secret = db.Column(db.String(255))
    zoho_access_token = db.Column(db.String(255))
    zoho_refresh_token = db.Column(db.String(255))
    zoho_token_expires_at = db.Column(db.DateTime)
    zoho_organization_id = db.Column(db.String(255))
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        if not self._is_strong_password(password):
            raise ValueError(
                "Password must be at least 8 characters long and contain:\n"
                "- At least one uppercase letter\n"
                "- At least one lowercase letter\n"
                "- At least one number\n"
                "- At least one special character"
            )
        self.password_hash = generate_password_hash(password)
    
    def _is_strong_password(self, password):
        """Check if password meets strength requirements."""
        if len(password) < 8:
            return False
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            return False
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            return False
        
        # Check for at least one number
        if not re.search(r'[0-9]', password):
            return False
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        
        return True
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_code(self):
        """Generate a 6-digit verification code."""
        self.verification_code = ''.join(secrets.choice(string.digits) for _ in range(6))
        self.verification_code_expires_at = datetime.utcnow() + timedelta(minutes=15)
        self.save()
    
    def verify_code(self, code):
        """Verify the code and activate user if correct."""
        if (self.verification_code == code and 
            self.verification_code_expires_at and 
            datetime.utcnow() < self.verification_code_expires_at):
            self.is_verified = True
            self.is_active = True
            self.verification_code = None
            self.verification_code_expires_at = None
            self.save()
            return True
        return False
    
    def save(self):
        """Save user to database."""
        db.session.add(self)
        db.session.commit()
    
    def to_dict(self):
        """Convert user to dictionary."""
        data = super().to_dict()
        data.update({
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'is_verified': self.is_verified,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications,
            'in_app_notifications': self.in_app_notifications
        })
        return data
    
    def __repr__(self):
        """String representation of the user."""
        return f'<User {self.username}>'

    def get_password_reset_token(self, expires_in=3600):
        """Generate a password reset token."""
        return jwt.encode(
            {
                'reset_password': self.id,
                'email': self.email,
                'exp': time() + expires_in,
                'used': False
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    def invalidate_reset_token(self):
        """Invalidate any existing password reset tokens."""
        self.password_reset_token = None
        db.session.commit()

    @staticmethod
    def verify_password_reset_token(token, invalidate=True):
        """Verify password reset token and optionally mark it as used."""
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'],
                               algorithms=['HS256'])
            id = payload['reset_password']
            email = payload.get('email')
            used = payload.get('used', False)
            exp = payload.get('exp')
            
            current_app.logger.info(f"Verifying password reset token for user {id}")
            current_app.logger.debug(f"Token payload: {payload}")
            
            # Check if token has expired
            if exp and time() > exp:
                current_app.logger.warning(f"Token has expired for user {id}")
                return None
                
            # Check if token has already been used
            if used:
                current_app.logger.warning(f"Token has already been used for user {id}")
                return None
                
            user = User.query.get(id)
            if not user:
                current_app.logger.warning(f"User {id} not found")
                return None
                
            # Verify that the email matches
            if user.email != email:
                current_app.logger.warning(f"Email mismatch for user {id}. Token email: {email}, User email: {user.email}")
                return None
                
            # Verify that the token matches what's stored in the database
            if user.password_reset_token != token:
                current_app.logger.warning(f"Token mismatch for user {id}")
                return None
                
            # Invalidate the token if requested
            if invalidate:
                user.password_reset_token = None
                db.session.commit()
                current_app.logger.info(f"Token invalidated for user {id}")
                
            return user
        except jwt.ExpiredSignatureError:
            current_app.logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            current_app.logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            current_app.logger.error(f"Error verifying token: {str(e)}")
            return None 