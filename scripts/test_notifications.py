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

def test_notification_generation():
    """Test notification generation for different expiry scenarios."""
    app = create_app()
    app.config['NOTIFICATION_DAYS'] = [30, 15, 7, 3, 1]  # Set notification days
    
    with app.app_context():
        # Get or create a test user
        user = User.query.filter_by(email='test@example.com').first()
        if not user:
            user = User(
                username='testuser',
                email='test@example.com'
            )
            user.password = 'Test123!'  # This will set the password_hash
            user.in_app_notifications = True
            user.email_notifications = False
            user.sms_notifications = False
            user.save()
        
        print("\n=== Test User ===")
        print(f"Username: {user.username}")
        print(f"In-app notifications: {user.in_app_notifications}")
        print(f"Email notifications: {user.email_notifications}")
        print(f"SMS notifications: {user.sms_notifications}")
        
        # Clear existing test items and notifications
        Item.query.filter_by(user_id=user.id).delete()
        Notification.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        # Create test items with different expiry dates
        today = datetime.now().date()
        test_items = [
            # Item expiring in 30 days
            {'name': 'Test Item 30 Days', 'expiry_date': today + timedelta(days=30)},
            # Item expiring in 15 days
            {'name': 'Test Item 15 Days', 'expiry_date': today + timedelta(days=15)},
            # Item expiring in 7 days
            {'name': 'Test Item 7 Days', 'expiry_date': today + timedelta(days=7)},
            # Item expiring in 3 days
            {'name': 'Test Item 3 Days', 'expiry_date': today + timedelta(days=3)},
            # Item expiring in 1 day
            {'name': 'Test Item 1 Day', 'expiry_date': today + timedelta(days=1)},
            # Item expiring in 4 days (should not generate notification)
            {'name': 'Test Item 4 Days', 'expiry_date': today + timedelta(days=4)},
        ]
        
        print("\n=== Creating Test Items ===")
        for item_data in test_items:
            item = Item(
                name=item_data['name'],
                expiry_date=item_data['expiry_date'],
                user_id=user.id,
                quantity=10
            )
            item.save()
            print(f"Created: {item.name} (Expires in {item.days_until_expiry} days)")
        
        # Run notification check
        print("\n=== Running Notification Check ===")
        notification_service = NotificationService()
        notifications = notification_service.check_expiry_dates()
        
        # Print results
        print("\n=== Notification Test Results ===")
        print(f"Total notifications generated: {len(notifications)}")
        print("\nGenerated Notifications:")
        for notification in notifications:
            print(f"- {notification.message} (Priority: {notification.priority}, Status: {notification.status})")
        
        # Verify no duplicates
        print("\n=== Duplicate Check ===")
        notification_service.check_expiry_dates()  # Run again to check for duplicates
        new_notifications = Notification.query.filter_by(user_id=user.id).all()
        print(f"Total notifications after second run: {len(new_notifications)}")
        if len(new_notifications) == len(notifications):
            print("✅ No duplicate notifications created")
        else:
            print("❌ Duplicate notifications detected!")
        
        # Test notification preferences
        print("\n=== Testing Notification Preferences ===")
        user.in_app_notifications = False
        user.save()
        print("Disabled in-app notifications")
        
        notifications = notification_service.get_user_notifications(user.id)
        print(f"Notifications with in-app disabled: {len(notifications)}")
        
        user.in_app_notifications = True
        user.save()
        print("Re-enabled in-app notifications")
        
        notifications = notification_service.get_user_notifications(user.id)
        print(f"Notifications with in-app enabled: {len(new_notifications)}")

if __name__ == '__main__':
    test_notification_generation() 