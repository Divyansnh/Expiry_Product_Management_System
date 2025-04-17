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
from app.tasks.cleanup import cleanup_expired_items
import logging

class TestConfig(Config):
    """Test configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    NOTIFICATION_DAYS = [30, 15, 7, 3, 1]

def test_notifications():
    """Test both daily notifications and cleanup notifications using a test database."""
    # Create app with test config
    app = create_app('testing')
    
    with app.app_context():
        # Create test user
        test_user = User(
            username='test_user',
            email='test@example.com'
        )
        test_user.password = 'Test123!'  # Use password property setter
        test_user.email_notifications = True  # Enable email notifications
        db.session.add(test_user)
        db.session.commit()
        
        print("\n=== Testing Daily Notifications ===")
        notification_service = NotificationService()
        
        # Create test items with different expiry dates
        today = datetime.now().date()
        test_items = [
            ('Test Item 1', today + timedelta(days=1)),  # Expires tomorrow
            ('Test Item 2', today + timedelta(days=3)),  # Expires in 3 days
            ('Test Item 3', today + timedelta(days=7)),  # Expires in 7 days
        ]
        
        for name, expiry_date in test_items:
            item = Item(
                name=name,
                description=f"Test {name}",
                quantity=1,
                unit="piece",
                purchase_date=today,
                expiry_date=expiry_date,
                user_id=test_user.id
            )
            db.session.add(item)
        
        db.session.commit()
        
        # Test daily notifications
        notification_service.check_expiry_dates()
        
        print("\n=== Testing Cleanup Notifications ===")
        # Run cleanup to trigger notifications
        cleanup_expired_items()
        
        # Check notifications
        notifications = notification_service.get_user_notifications(test_user.id)
        print(f"\nFound {len(notifications)} notifications:")
        for notification in notifications:
            print(f"- {notification.message} (Status: {notification.status}, Priority: {notification.priority})")
        
        # Clean up test data
        Notification.query.filter_by(user_id=test_user.id).delete()
        Item.query.filter_by(user_id=test_user.id).delete()
        db.session.delete(test_user)
        db.session.commit()
        print("\nCleaned up all test data")

if __name__ == "__main__":
    test_notifications() 