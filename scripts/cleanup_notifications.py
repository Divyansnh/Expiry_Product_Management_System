import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.notification import Notification
from sqlalchemy import func
from app.core.extensions import db

def cleanup_duplicate_notifications():
    """Clean up duplicate notifications, keeping only the most recent one per item per day."""
    app = create_app()
    
    with app.app_context():
        # Find items with duplicate notifications on the same day
        duplicates = db.session.query(
            Notification.item_id,
            func.date(Notification.created_at)
        ).group_by(
            Notification.item_id,
            func.date(Notification.created_at)
        ).having(
            func.count('*') > 1
        ).all()
        
        total_deleted = 0
        
        # For each set of duplicates
        for item_id, date in duplicates:
            # Get all notifications for this item on this date
            notifications = Notification.query.filter(
                Notification.item_id == item_id,
                func.date(Notification.created_at) == date
            ).order_by(
                Notification.created_at.desc()
            ).all()
            
            # Keep the most recent one, delete the rest
            for notification in notifications[1:]:
                db.session.delete(notification)
                total_deleted += 1
        
        # Commit changes
        db.session.commit()
        print(f'Cleaned up {len(duplicates)} sets of duplicate notifications')
        print(f'Total notifications deleted: {total_deleted}')

if __name__ == '__main__':
    cleanup_duplicate_notifications() 