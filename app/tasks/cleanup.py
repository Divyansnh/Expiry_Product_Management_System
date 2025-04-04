from datetime import datetime, timedelta
from app.core.extensions import db
from app.models.item import Item
from app.models.notification import Notification
from app.services.zoho_service import ZohoService
from flask import current_app

def cleanup_expired_items():
    """Cleanup expired items and send notifications."""
    try:
        current_date = datetime.now().date()
        yesterday = current_date - timedelta(days=1)
        
        # Find items that expired yesterday using filter_by
        expired_items = Item.query.filter_by(
            expiry_date=yesterday,
            status='Expired'
        ).all()
        
        for item in expired_items:
            # Create notification for the user
            notification = Notification(
                user_id=item.user_id,
                message=f"Item '{item.name}' (ID: {item.id}) has expired and will be removed from the system."
            )
            db.session.add(notification)
            
            # Mark item as inactive in Zoho if it has a Zoho ID
            if item.zoho_item_id:
                try:
                    # Get the user associated with the item
                    user = item.user
                    if user:
                        zoho_service = ZohoService(user)
                        zoho_service.delete_item_in_zoho(item.zoho_item_id)
                except Exception as e:
                    current_app.logger.error(f"Error deleting item from Zoho: {str(e)}")
            
            # Remove item from database
            db.session.delete(item)
        
        db.session.commit()
        current_app.logger.info(f"Successfully cleaned up {len(expired_items)} expired items")
        
    except Exception as e:
        current_app.logger.error(f"Error cleaning up expired items: {str(e)}")
        db.session.rollback() 