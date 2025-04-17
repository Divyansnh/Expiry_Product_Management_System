import os
import sys
from datetime import datetime, timedelta
import time

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)

from app import create_app
from app.models.item import Item
from app.models.user import User
from app.models.notification import Notification
from app.core.extensions import db
from app.tasks.cleanup import cleanup_expired_items
from app.core.config import Config

class TestConfig(Config):
    """Test configuration."""
    SCHEDULER_API_ENABLED = False

# Create a single app instance for all tests
app = create_app(TestConfig)

def setup_test():
    """Create test data and return the test user."""
    with app.app_context():
        # Create a test user
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            test_user = User()
            test_user.username = 'testuser'
            test_user.email = 'test@example.com'
            test_user.set_password('testpass')
            test_user.save()
            print(f"Created test user: {test_user.username}")
        
        # Create items with different dates
        yesterday = datetime.now().date() - timedelta(days=1)
        today = datetime.now().date()
        tomorrow = datetime.now().date() + timedelta(days=1)
        
        # Create expired item (yesterday)
        expired_item = Item()
        expired_item.name = 'Test Expired Item'
        expired_item.expiry_date = yesterday
        expired_item.status = 'Expired'
        expired_item.user_id = test_user.id
        db.session.add(expired_item)
        
        # Create item expiring today
        today_item = Item()
        today_item.name = 'Test Today Item'
        today_item.expiry_date = today
        today_item.status = 'Expiring Soon'
        today_item.user_id = test_user.id
        db.session.add(today_item)
        
        # Create future item
        future_item = Item()
        future_item.name = 'Test Future Item'
        future_item.expiry_date = tomorrow
        future_item.status = 'Active'
        future_item.user_id = test_user.id
        db.session.add(future_item)
        
        db.session.commit()
        
        print("\nTest data created:")
        print(f"1. Expired Item (Yesterday): {expired_item.name}")
        print(f"2. Today's Item: {today_item.name}")
        print(f"3. Future Item: {future_item.name}")
        
        return test_user.id

def check_notifications(user_id):
    """Check notifications created for the user."""
    with app.app_context():
        notifications = Notification.query.filter_by(user_id=user_id).all()
        print("\nNotifications:")
        for notif in notifications:
            print(f"- {notif.message} (Priority: {notif.priority})")
        return len(notifications)

def verify_cleanup():
    """Run cleanup and verify results."""
    with app.app_context():
        # Get initial counts
        initial_items = Item.query.count()
        initial_expired = Item.query.filter_by(status='Expired').count()
        
        print(f"\nBefore cleanup:")
        print(f"Total items: {initial_items}")
        print(f"Expired items: {initial_expired}")
        
        # Run cleanup
        print("\nRunning cleanup...")
        cleanup_expired_items()
        
        # Get final counts
        final_items = Item.query.count()
        final_expired = Item.query.filter_by(status='Expired').count()
        
        print(f"\nAfter cleanup:")
        print(f"Total items: {final_items}")
        print(f"Expired items: {final_expired}")
        
        # Show remaining items
        remaining_items = Item.query.all()
        print("\nRemaining items:")
        for item in remaining_items:
            print(f"- {item.name} (Status: {item.status}, Expiry: {item.expiry_date})")

def cleanup_test_data(user_id):
    """Clean up all test data."""
    with app.app_context():
        try:
            # Get all items for the test user
            items = Item.query.filter_by(user_id=user_id).all()
            item_ids = [item.id for item in items]
            
            # Delete notifications
            Notification.query.filter(
                (Notification.item_id.in_(item_ids)) |
                (Notification.user_id == user_id)
            ).delete(synchronize_session=False)
            
            # Delete items
            Item.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            
            # Delete user
            User.query.filter_by(id=user_id).delete()
            
            db.session.commit()
            print("\nTest data cleaned up successfully!")
        except Exception as e:
            print(f"Error cleaning up test data: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    print("Starting real-time cleanup test...")
    
    # Setup test data
    user_id = setup_test()
    
    # Check initial notifications
    print("\nChecking initial notifications...")
    initial_notifications = check_notifications(user_id)
    
    # Run and verify cleanup
    verify_cleanup()
    
    # Check notifications after cleanup
    print("\nChecking notifications after cleanup...")
    final_notifications = check_notifications(user_id)
    
    print(f"\nNotification Summary:")
    print(f"- Initial notifications: {initial_notifications}")
    print(f"- Final notifications: {final_notifications}")
    print(f"- New notifications created: {final_notifications - initial_notifications}")
    
    # Clean up test data
    cleanup_test_data(user_id)
    
    print("\nTest completed!") 