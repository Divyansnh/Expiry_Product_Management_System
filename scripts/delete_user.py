import os
import sys
from app import create_app
from app.models.user import User
from app.models.item import Item
from app.models.report import Report
from app.models.notification import Notification
from app.core.extensions import db

def delete_user(username: str):
    """Delete a user by username."""
    print(f"\nAttempting to delete user: {username}")
    
    # Create app with production config
    app = create_app('production')
    
    with app.app_context():
        try:
            # Find the user
            user = User.query.filter_by(username=username).first()
            
            if not user:
                print(f"User '{username}' not found")
                return
            
            # Delete associated items
            Item.query.filter_by(user_id=user.id).delete()
            
            # Delete associated reports
            Report.query.filter_by(user_id=user.id).delete()
            
            # Delete associated notifications
            Notification.query.filter_by(user_id=user.id).delete()
            
            # Delete the user
            db.session.delete(user)
            db.session.commit()
            
            print(f"User '{username}' and all associated data deleted successfully")
            
        except Exception as e:
            print(f"Error deleting user: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python delete_user.py <username>")
        sys.exit(1)
    
    delete_user(sys.argv[1]) 