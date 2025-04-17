import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import User
from app.models.item import Item
from app.models.notification import Notification
from app.core.extensions import db, scheduler
from app.services.notification_service import NotificationService
from datetime import datetime, timedelta

def check_database():
    """Check if any test data exists in the actual database."""
    app = create_app()
    
    with app.app_context():
        print('=== Checking Database for Test Data ===')
        
        # Check for test user
        test_user = User.query.filter_by(username='testuser', email='test@example.com').first()
        print('\n=== Test User ===')
        print(f'Test user exists: {test_user is not None}')
        
        # Check for test items
        test_items = Item.query.filter(Item.name.like('Test Item%')).all()
        print('\n=== Test Items ===')
        print(f'Number of test items found: {len(test_items)}')
        if test_items:
            print('Test items found:')
            for item in test_items:
                print(f'- {item.name} (ID: {item.id})')
        
        # Check for test notifications
        test_notifications = Notification.query.filter(
            Notification.message.like('%Test Item%')
        ).all()
        print('\n=== Test Notifications ===')
        print(f'Number of test notifications found: {len(test_notifications)}')
        if test_notifications:
            print('Test notifications found:')
            for notif in test_notifications:
                print(f'- {notif.message}')

def test_duplicate_notifications():
    """Test duplicate notification prevention in an in-memory database."""
    # Create test configuration
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SCHEDULER_API_ENABLED = False
        SCHEDULER_RUN = False
        NOTIFICATION_DAYS = [30, 15, 7, 3, 1]
        WTF_CSRF_ENABLED = False
    
    # Stop the scheduler if it's running
    if scheduler.running:
        scheduler.shutdown()
    
    # Create a test app with in-memory database
    test_app = create_app('testing')
    test_app.config.from_object(TestConfig)
    
    with test_app.app_context():
        print('\n=== Testing Duplicate Notification Prevention ===')
        
        # Create tables in the in-memory database
        db.create_all()
        
        try:
            # Create a test user
            test_user = User(
                username='testuser_duplicate',
                email='test_duplicate@example.com'
            )
            test_user.password = 'Test123!@'
            test_user.email_notifications = True
            db.session.add(test_user)
            db.session.commit()
            
            # Create a test item
            test_item = Item(
                name='Test Item for Duplicate Check',
                expiry_date=datetime.now() + timedelta(days=1),  # Expires in 1 day
                user_id=test_user.id,
                status='active'
            )
            db.session.add(test_item)
            db.session.commit()
            
            # Create notification service
            notification_service = NotificationService()
            
            # First notification check
            print('\nRunning first notification check...')
            notifications1 = notification_service.check_expiry_dates()
            print(f'Created {len(notifications1)} notifications')
            for notif in notifications1:
                print(f'- {notif.message}')
            
            # Second notification check (should not create duplicates)
            print('\nRunning second notification check...')
            notifications2 = notification_service.check_expiry_dates()
            print(f'Created {len(notifications2)} notifications')
            for notif in notifications2:
                print(f'- {notif.message}')
            
            # Verify total notifications
            all_notifications = Notification.query.filter_by(
                user_id=test_user.id,
                item_id=test_item.id
            ).all()
            print(f'\nTotal notifications in database: {len(all_notifications)}')
            
            if len(all_notifications) == 1:
                print('✅ Success: No duplicate notifications were created')
            else:
                print('❌ Error: Duplicate notifications were created')
            
        finally:
            # Clean up in-memory database
            db.session.remove()
            db.drop_all()

if __name__ == '__main__':
    check_database()
    test_duplicate_notifications() 