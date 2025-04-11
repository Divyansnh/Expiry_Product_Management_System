import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app import create_app
from app.models.notification import Notification
from app.core.extensions import db
from sqlalchemy import and_, cast
from sqlalchemy.sql.expression import BinaryExpression

def cleanup_duplicate_notifications():
    """Clean up duplicate notifications."""
    app = create_app()
    
    with app.app_context():
        try:
            # Get all notifications
            notifications = Notification.query.all()
            print(f"Total notifications before cleanup: {len(notifications)}")
            
            # Group notifications by user_id, item_id, message, and type
            notification_groups = {}
            for notification in notifications:
                key = (
                    notification.user_id,
                    notification.item_id,
                    notification.message,
                    notification.type
                )
                if key not in notification_groups:
                    notification_groups[key] = []
                notification_groups[key].append(notification)
            
            # Find and delete duplicates
            deleted_count = 0
            for key, group in notification_groups.items():
                if len(group) > 1:
                    # Sort by created_at to keep the most recent one
                    group.sort(key=lambda x: x.created_at, reverse=True)
                    # Keep the most recent notification
                    keep = group[0]
                    # Delete all others
                    for notification in group[1:]:
                        # Only delete if within 24 hours of the most recent one
                        if (keep.created_at - notification.created_at) <= timedelta(days=1):
                            db.session.delete(notification)
                            deleted_count += 1
            
            db.session.commit()
            print(f"Deleted {deleted_count} duplicate notifications")
            
            # Verify cleanup
            remaining_notifications = Notification.query.all()
            print(f"Total notifications after cleanup: {len(remaining_notifications)}")
            
        except Exception as e:
            print(f"Error cleaning up notifications: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    cleanup_duplicate_notifications() 