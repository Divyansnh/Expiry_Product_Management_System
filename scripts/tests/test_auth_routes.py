import os
import sys
import time
from datetime import datetime, timedelta
import unittest
from unittest.mock import patch
from flask import url_for, Flask, session
from werkzeug.security import generate_password_hash
from app.routes.auth import generate_password_reset_token

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import create_app, db
from app.models.user import User
from app.services.email_service import EmailService
from app.config import Config

class TestConfig(Config):
    """Test configuration."""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key-123'
    SCHEDULER_API_ENABLED = False
    SCHEDULER_RUN = False
    SCHEDULER_JOBS = []
    
    # Email settings
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = 'test@example.com'

class TestAuthRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Create test users
        self.test_user = User(
            username='testuser',
            email='test@example.com',
            is_verified=True
        )
        self.test_user.set_password('password123')
        db.session.add(self.test_user)
        
        self.unverified_user = User(
            username='unverified',
            email='unverified@example.com',
            is_verified=False
        )
        self.unverified_user.set_password('password123')
        db.session.add(self.unverified_user)
        
        db.session.commit()
        
        # Mock email service
        self.email_service_patcher = patch('app.services.email_service.EmailService.send_email')
        self.mock_send_email = self.email_service_patcher.start()
        self.mock_send_email.return_value = True

    def tearDown(self):
        """Clean up test environment."""
        self.email_service_patcher.stop()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_valid_registration(self):
        """Test successful user registration."""
        with self.app.app_context():
            response = self.client.post('/auth/register', data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'StrongPass123!@#',
                'confirm_password': 'StrongPass123!@#'
            }, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Registration successful', response.data)
            
            # Verify user was created
            user = User.query.filter_by(email='new@example.com').first()
            self.assertIsNotNone(user)
            self.assertFalse(user.is_verified)

    def test_duplicate_registration(self):
        """Test registration with duplicate email/username."""
        with self.app.app_context():
            # Test duplicate email
            response = self.client.post('/auth/register', data={
                'username': 'differentuser',
                'email': 'test@example.com',
                'password': 'StrongPass123!@#',
                'confirm_password': 'StrongPass123!@#'
            })
            self.assertIn(b'Email already registered', response.data)
            
            # Test duplicate username
            response = self.client.post('/auth/register', data={
                'username': 'testuser',
                'email': 'different@example.com',
                'password': 'StrongPass123!@#',
                'confirm_password': 'StrongPass123!@#'
            })
            self.assertIn(b'Username already taken', response.data)

    def test_weak_password_registration(self):
        """Test registration with weak passwords."""
        weak_passwords = [
            'short',  # Too short
            'nouppercase123!',  # No uppercase
            'NOLOWERCASE123!',  # No lowercase
            'NoNumbers!@#',  # No numbers
            'NoSpecial123'  # No special characters
        ]
        
        with self.app.app_context():
            for password in weak_passwords:
                response = self.client.post('/auth/register', data={
                    'username': f'user{password}',
                    'email': f'user{password}@example.com',
                    'password': password,
                    'confirm_password': password
                })
                self.assertIn(b'Password must be at least 8 characters', response.data)

    def test_valid_login(self):
        """Test successful login."""
        with self.app.app_context():
            response = self.client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'password123',
                'remember_me': True
            }, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Dashboard', response.data)

    def test_invalid_login(self):
        """Test login with invalid credentials."""
        with self.app.app_context():
            # Wrong password
            response = self.client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'WrongPass123!@#'
            })
            self.assertIn(b'Invalid email or password', response.data)
            
            # Non-existent email
            response = self.client.post('/auth/login', data={
                'email': 'nonexistent@example.com',
                'password': 'password123'
            })
            self.assertIn(b'Invalid email or password', response.data)

    def test_unverified_login(self):
        """Test login with unverified account."""
        with self.app.app_context():
            response = self.client.post('/auth/login', data={
                'email': 'unverified@example.com',
                'password': 'password123'
            }, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            with self.client.session_transaction() as session:
                self.assertEqual(session.get('pending_verification_email'), 'unverified@example.com')

    def test_email_verification(self):
        """Test email verification flow."""
        with self.app.app_context():
            # Create new unverified user
            user = User(
                username='verifytest',
                email='verify@example.com',
                is_verified=False
            )
            user.set_password('Test123!@#')
            user.verification_code = '123456'  # Set a known verification code
            user.verification_code_expires = datetime.utcnow() + timedelta(hours=1)
            db.session.add(user)
            db.session.commit()
            
            # Set up session with pending verification email
            with self.client.session_transaction() as session:
                session['pending_verification_email'] = user.email
            
            # Test invalid verification code
            response = self.client.post('/auth/verify-email', data={
                'verification_code': '000000'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Invalid verification code', response.data)
            
            # Test valid verification code
            response = self.client.post('/auth/verify-email', data={
                'verification_code': '123456'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Email verified successfully', response.data)
            
            # Verify user is now verified
            user = User.query.filter_by(email='verify@example.com').first()
            self.assertTrue(user.is_verified)

    def test_password_reset(self):
        """Test password reset flow."""
        with self.app.app_context():
            # Request password reset
            response = self.client.post('/auth/reset_password_request', data={
                'email': 'test@example.com'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            
            # Get reset token
            user = User.query.filter_by(email='test@example.com').first()
            token = user.get_password_reset_token()
            
            # Reset password
            response = self.client.post(f'/auth/reset_password/{token}', data={
                'password': 'NewPass123!@#',
                'password2': 'NewPass123!@#'  # Match the form field name
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Your password has been reset', response.data)
            
            # Verify new password works
            response = self.client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'NewPass123!@#'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            with self.client.session_transaction() as session:
                self.assertIn('_user_id', session)

    def test_session_handling(self):
        """Test session handling during login and logout."""
        # Test login
        response = self.client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        with self.client.session_transaction() as session:
            self.assertIn('_user_id', session)
            self.assertEqual(session['_user_id'], str(self.test_user.id))
        
        # Test logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        with self.client.session_transaction() as session:
            self.assertNotIn('_user_id', session)

if __name__ == '__main__':
    unittest.main() 