import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app import create_app
from app.models.user import User
from app.models.item import Item
from app.models.notification import Notification
from app.services.notification_service import NotificationService
from app.core.extensions import db
from app.core.config import Config
import logging

class TestConfig(Config):
    """Test configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    NOTIFICATION_DAYS = [30, 15, 7, 3, 1]

def test_notifications():
    """Test the notification system."""
    # Create app with testing config
    app = create_app('testing')
    
    with app.app_context():
        # Create test user
        test_user = User(
            username='test_user',
            email='test@example.com'
        )
        test_user.password = 'Test123!'  # Use password property setter
        test_user.email_notifications = True
        db.session.add(test_user)
        db.session.commit()
        
        # Create test items with different expiry dates
        today = datetime.utcnow().date()
        test_items = [
            ('Item 1', today + timedelta(days=1)),  # Expires in 1 day
            ('Item 2', today + timedelta(days=3)),  # Expires in 3 days
            ('Item 3', today + timedelta(days=7)),  # Expires in 7 days
            ('Item 4', today + timedelta(days=15)),  # Expires in 15 days
            ('Item 5', today + timedelta(days=30)),  # Expires in 30 days
            ('Item 6', today - timedelta(days=1)),  # Already expired
        ]
        
        for name, expiry_date in test_items:
            item = Item(
                name=name,
                expiry_date=expiry_date,
                user_id=test_user.id
            )
            db.session.add(item)
        
        db.session.commit()
        
        # Run notification check
        notification_service = NotificationService()
        notification_service.check_expiry_dates()
        
        # Print created notifications
        notifications = Notification.query.filter_by(user_id=test_user.id).all()
        print("\nCreated Notifications:")
        for notification in notifications:
            print(f"- {notification.message} (Type: {notification.type}, Priority: {notification.priority})")
        
        # Clean up
        db.session.delete(test_user)
        db.session.commit()

if __name__ == '__main__':
    test_notifications() 