import os
import sys
from datetime import datetime, timedelta
import time

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models.user import User
from app.models.item import Item
from app.models.notification import Notification
from app.tasks.cleanup import cleanup_unverified_accounts

def verify_cleanup_in_production():
    """Verify the cleanup task in the actual application."""
    print("\nStarting production cleanup verification...")
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Create test data
            print("\nCreating test data...")
            
            # Create an unverified user with creation time 2 hours ago
            test_user = User()
            test_user.username = "test_unverified_user"
            test_user.email = "test_unverified@example.com"
            test_user.password = "Test@123"  # This will trigger the password setter
            test_user.is_verified = False
            test_user.created_at = datetime.utcnow() - timedelta(hours=2)
            
            # Create some test items
            test_item1 = Item()
            test_item1.name = "Test Item 1"
            test_item1.description = "Test Description 1"
            test_item1.selling_price = 10.0
            test_item1.user_id = None  # Will be set after user is created
            
            test_item2 = Item()
            test_item2.name = "Test Item 2"
            test_item2.description = "Test Description 2"
            test_item2.selling_price = 20.0
            test_item2.user_id = None  # Will be set after user is created
            
            # Create a test notification
            test_notification = Notification(
                message="Test Notification",
                user_id=None  # Will be set after user is created
            )
            
            # Add all to database
            db.session.add(test_user)
            db.session.commit()  # Commit to get user ID
            
            # Set user_id for items and notification
            test_item1.user_id = test_user.id
            test_item2.user_id = test_user.id
            test_notification.user_id = test_user.id
            
            # Add items and notification
            db.session.add(test_item1)
            db.session.add(test_item2)
            db.session.add(test_notification)
            db.session.commit()
            
            # Get the user ID for verification
            user_id = test_user.id
            
            print(f"Created test user with ID: {user_id}")
            print("Created 2 items and 1 notification for the test user")
            
            # Verify initial state
            print("\nVerifying initial state:")
            user_exists = User.query.get(user_id) is not None
            items_count = Item.query.filter_by(user_id=user_id).count()
            notifications_count = Notification.query.filter_by(user_id=user_id).count()
            
            print(f"User exists: {user_exists}")
            print(f"Items count: {items_count}")
            print(f"Notifications count: {notifications_count}")
            
            # Run cleanup task
            print("\nRunning cleanup task...")
            cleanup_unverified_accounts()
            
            # Verify cleanup
            print("\nVerifying cleanup:")
            user_exists = User.query.get(user_id) is not None
            items_count = Item.query.filter_by(user_id=user_id).count()
            notifications_count = Notification.query.filter_by(user_id=user_id).count()
            
            print(f"User exists: {user_exists}")
            print(f"Items count: {items_count}")
            print(f"Notifications count: {notifications_count}")
            
            if not user_exists and items_count == 0 and notifications_count == 0:
                print("\n✅ Cleanup successful in production!")
            else:
                print("\n❌ Cleanup failed in production!")
            
        except Exception as e:
            print(f"\n❌ Error during verification: {str(e)}")
            db.session.rollback()
        finally:
            # Clean up any remaining test data
            try:
                User.query.filter_by(username="test_unverified_user").delete()
                db.session.commit()
            except:
                db.session.rollback()

if __name__ == "__main__":
    verify_cleanup_in_production() 