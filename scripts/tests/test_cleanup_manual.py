import os
import sys
from datetime import datetime, timedelta

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)

from app import create_app
from app.models.item import Item
from app.models.user import User
from app.models.notification import Notification
from app.core.extensions import db
from app.tasks.cleanup import cleanup_expired_items

# Create a single app instance
app = create_app()

def create_test_data():
    """Create test data for cleanup testing."""
    with app.app_context():
        try:
            # Create a test user if not exists
            test_user = User.query.filter_by(email='test@example.com').first()
            if not test_user:
                test_user = User()
                test_user.username = 'testuser'
                test_user.email = 'test@example.com'
                test_user.set_password('testpass')
                test_user.save()

            # Create test items with different expiry dates
            yesterday = datetime.now().date() - timedelta(days=1)
            today = datetime.now().date()
            tomorrow = datetime.now().date() + timedelta(days=1)

            # Item that should be cleaned up (expired yesterday)
            expired_item = Item()
            expired_item.name = 'Test Expired Item'
            expired_item.expiry_date = yesterday
            expired_item.status = 'Expired'
            expired_item.user_id = test_user.id
            db.session.add(expired_item)

            # Item that should not be cleaned up (expires tomorrow)
            active_item = Item()
            active_item.name = 'Test Active Item'
            active_item.expiry_date = tomorrow
            active_item.status = 'Active'
            active_item.user_id = test_user.id
            db.session.add(active_item)

            db.session.commit()
            print("Test data created successfully!")
            print(f"- Created user: {test_user.username}")
            print(f"- Created expired item: {expired_item.name}")
            print(f"- Created active item: {active_item.name}")

        except Exception as e:
            print(f"Error creating test data: {str(e)}")
            db.session.rollback()

def run_cleanup_test():
    """Run the cleanup task and verify results."""
    with app.app_context():
        try:
            # Get initial counts
            initial_expired_count = Item.query.filter_by(status='Expired').count()
            initial_total_count = Item.query.count()
            
            print("\nBefore cleanup:")
            print(f"Total items: {initial_total_count}")
            print(f"Expired items: {initial_expired_count}")

            # Run cleanup
            print("\nRunning cleanup task...")
            cleanup_expired_items()

            # Get counts after cleanup
            final_expired_count = Item.query.filter_by(status='Expired').count()
            final_total_count = Item.query.count()
            
            print("\nAfter cleanup:")
            print(f"Total items: {final_total_count}")
            print(f"Expired items: {final_expired_count}")
            
            # Verify results
            if final_expired_count < initial_expired_count:
                print("\n✅ Cleanup successful! Expired items were removed.")
            else:
                print("\n❌ Cleanup may not have worked as expected.")

        except Exception as e:
            print(f"Error during cleanup test: {str(e)}")
            db.session.rollback()

def cleanup_test_data():
    """Clean up test data after testing."""
    with app.app_context():
        try:
            # Remove test user and all associated items
            test_user = User.query.filter_by(email='test@example.com').first()
            if test_user:
                # Get all items for the test user
                test_items = Item.query.filter_by(user_id=test_user.id).all()
                item_ids = [item.id for item in test_items]
                
                # Delete all notifications, including those created during cleanup
                Notification.query.filter(
                    (Notification.item_id.in_(item_ids)) |
                    (Notification.user_id == test_user.id)
                ).delete(synchronize_session=False)
                
                # Delete all items
                Item.query.filter_by(user_id=test_user.id).delete(synchronize_session=False)
                
                # Finally delete the test user
                db.session.delete(test_user)
                db.session.commit()
                print("\nTest data cleaned up successfully!")
        except Exception as e:
            print(f"Error cleaning up test data: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    print("Starting manual cleanup test...")
    
    # Create test data
    create_test_data()
    
    # Run cleanup test
    run_cleanup_test()
    
    # Clean up test data
    cleanup_test_data()
    
    print("\nTest completed!") 