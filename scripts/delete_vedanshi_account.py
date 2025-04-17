import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import User
from app.models.item import Item
from app.models.notification import Notification
from app.core.extensions import db

app = create_app()

with app.app_context():
    try:
        # Find Vedanshi user
        user = User.query.filter_by(username='Vedanshi').first()
        
        if user:
            print(f"\nFound user:")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Created at: {user.created_at}")
            
            # Delete associated items
            items = Item.query.filter_by(user_id=user.id).all()
            for item in items:
                db.session.delete(item)
            print(f"\nDeleted {len(items)} items")
            
            # Delete associated notifications
            notifications = Notification.query.filter_by(user_id=user.id).all()
            for notification in notifications:
                db.session.delete(notification)
            print(f"Deleted {len(notifications)} notifications")
            
            # Delete the user
            db.session.delete(user)
            db.session.commit()
            print("\nSuccessfully deleted Vedanshi's account and all associated data.")
        else:
            print("\nNo user found with username 'Vedanshi'")
            
    except Exception as e:
        print(f"\nError deleting user: {str(e)}")
        db.session.rollback() 