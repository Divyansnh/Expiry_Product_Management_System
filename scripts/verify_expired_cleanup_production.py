import os
import sys
from datetime import datetime, timedelta

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models.user import User
from app.models.item import Item
from app.models.notification import Notification
from app.tasks.cleanup import cleanup_expired_items

def verify_expired_cleanup_in_production():
    """Verify the expired items cleanup task in the actual application."""
    print("\nStarting expired items cleanup verification...")
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Clean up any existing test data first
            print("\nCleaning up any existing test data...")
            test_user = User.query.filter_by(username="test_expired_user").first()
            if test_user:
                # Delete in correct order: notifications -> items -> user
                # First, get all items for this user
                items = Item.query.filter_by(user_id=test_user.id).all()
                for item in items:
                    # Delete notifications for each item
                    Notification.query.filter_by(item_id=item.id).delete()
                
                # Delete user's notifications that aren't linked to items
                Notification.query.filter_by(user_id=test_user.id, item_id=None).delete()
                
                # Now delete items
                Item.query.filter_by(user_id=test_user.id).delete()
                
                # Finally delete the user
                db.session.delete(test_user)
                db.session.commit()
            
            # Create test data
            print("\nCreating test data...")
            
            # Create a verified user
            test_user = User()
            test_user.username = "test_expired_user"
            test_user.email = "test_expired@example.com"
            test_user.password = "Test@123"
            test_user.is_verified = True
            
            # Create items with different expiry dates
            # 1. Expired item (yesterday)
            expired_item = Item()
            expired_item.name = "Expired Item"
            expired_item.description = "This item expired yesterday"
            expired_item.selling_price = 10.0
            expired_item.expiry_date = datetime.utcnow().date() - timedelta(days=1)
            expired_item.status = 'Expired'
            expired_item.user_id = None  # Will be set after user is created
            
            # 2. Expiring soon item (5 days from now)
            expiring_soon_item = Item()
            expiring_soon_item.name = "Expiring Soon Item"
            expiring_soon_item.description = "This item expires in 5 days"
            expiring_soon_item.selling_price = 20.0
            expiring_soon_item.expiry_date = datetime.utcnow().date() + timedelta(days=5)
            expiring_soon_item.status = 'Active'
            expiring_soon_item.user_id = None  # Will be set after user is created
            
            # 3. Active item (30 days from now)
            active_item = Item()
            active_item.name = "Active Item"
            active_item.description = "This item expires in 30 days"
            active_item.selling_price = 30.0
            active_item.expiry_date = datetime.utcnow().date() + timedelta(days=30)
            active_item.status = 'Active'
            active_item.user_id = None  # Will be set after user is created
            
            # Create notifications for the expired item
            expired_notification = Notification(
                message="Item has expired",
                user_id=None,  # Will be set after user is created
                item_id=None   # Will be set after item is created
            )
            
            expiring_notification = Notification(
                message="Item is expiring soon",
                user_id=None,  # Will be set after user is created
                item_id=None   # Will be set after item is created
            )
            
            # Add user to database
            db.session.add(test_user)
            db.session.commit()  # Commit to get user ID
            
            # Set user_id for items and notifications
            expired_item.user_id = test_user.id
            expiring_soon_item.user_id = test_user.id
            active_item.user_id = test_user.id
            
            # Add items to database
            db.session.add(expired_item)
            db.session.add(expiring_soon_item)
            db.session.add(active_item)
            db.session.commit()  # Commit to get item IDs
            
            # Set item_id and user_id for notifications
            expired_notification.user_id = test_user.id
            expired_notification.item_id = expired_item.id
            expiring_notification.user_id = test_user.id
            expiring_notification.item_id = expiring_soon_item.id
            
            # Add notifications to database
            db.session.add(expired_notification)
            db.session.add(expiring_notification)
            db.session.commit()
            
            # Get IDs for verification
            expired_item_id = expired_item.id
            expiring_soon_item_id = expiring_soon_item.id
            active_item_id = active_item.id
            
            print(f"Created test user with ID: {test_user.id}")
            print("Created 3 items (expired, expiring soon, active)")
            print("Created 2 notifications")
            
            # Verify initial state
            print("\nVerifying initial state:")
            expired_exists = Item.query.get(expired_item_id) is not None
            expiring_exists = Item.query.get(expiring_soon_item_id) is not None
            active_exists = Item.query.get(active_item_id) is not None
            notifications_count = Notification.query.filter_by(user_id=test_user.id).count()
            
            print(f"Expired item exists: {expired_exists}")
            print(f"Expiring soon item exists: {expiring_exists}")
            print(f"Active item exists: {active_exists}")
            print(f"Notifications count: {notifications_count}")
            
            # Run cleanup task
            print("\nRunning cleanup task...")
            cleanup_expired_items()
            
            # Verify cleanup
            print("\nVerifying cleanup:")
            expired_exists = Item.query.get(expired_item_id) is not None
            expiring_exists = Item.query.get(expiring_soon_item_id) is not None
            active_exists = Item.query.get(active_item_id) is not None
            notifications_count = Notification.query.filter_by(user_id=test_user.id).count()
            
            print(f"Expired item exists: {expired_exists}")
            print(f"Expiring soon item exists: {expiring_exists}")
            print(f"Active item exists: {active_exists}")
            print(f"Notifications count: {notifications_count}")
            
            if not expired_exists and expiring_exists and active_exists:
                print("\n✅ Cleanup successful in production!")
            else:
                print("\n❌ Cleanup failed in production!")
            
        except Exception as e:
            print(f"\n❌ Error during verification: {str(e)}")
            db.session.rollback()
        finally:
            # Clean up any remaining test data
            try:
                User.query.filter_by(username="test_expired_user").delete()
                db.session.commit()
            except:
                db.session.rollback()

if __name__ == "__main__":
    verify_expired_cleanup_in_production() 