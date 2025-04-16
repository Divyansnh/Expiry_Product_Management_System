from datetime import datetime, timedelta
from typing import List, Optional, Union, Dict, Any, Literal, TypedDict, Sequence, cast
from flask import current_app
from app.core.extensions import db
from app.models.notification import Notification
from app.models.item import Item, STATUS_EXPIRED
from app.models.user import User
from app.services.email_service import EmailService
from sqlalchemy import and_, not_, or_
from sqlalchemy.sql import expression
from sqlalchemy.sql.expression import BinaryExpression

class ItemNotification(TypedDict):
    name: str
    days_until_expiry: int
    priority: Literal['high', 'normal', 'low']

NotificationType = Literal['email']
NotificationPriority = Literal['high', 'normal', 'low']

class NotificationService:
    """Service for handling expiry notifications."""
    
    def __init__(self) -> None:
        self._notification_days: Optional[List[int]] = None
        self.email_service = EmailService()
    
    @property
    def notification_days(self) -> List[int]:
        """Get notification days from config."""
        if self._notification_days is None:
            config_days = current_app.config.get('NOTIFICATION_DAYS')
            if config_days is None:
                self._notification_days = []
            else:
                self._notification_days = list(config_days)  # Ensure it's a list
        return self._notification_days
    
    def check_expiry_dates(self) -> None:
        """Check all items for expiry dates and send email notifications."""
        try:
            current_app.logger.info("Starting expiry date check at %s", datetime.now())
            
            # Get all items with expiry dates that are not already expired
            items = Item.query.filter(
                and_(
                    cast(BinaryExpression, Item.expiry_date.isnot(None)),
                    cast(BinaryExpression, Item.status != STATUS_EXPIRED)
                )
            ).all()
            
            current_app.logger.info("Found %d items to check for notifications", len(items))
            
            # Group items by user
            user_items: Dict[int, List[Dict[str, Any]]] = {}
            
            for item in items:
                days_until_expiry = item.days_until_expiry
                if days_until_expiry is None:
                    continue
                    
                # Process all items for daily notification
                if item.user_id not in user_items:
                    user_items[item.user_id] = []
                
                # Set priority based on days until expiry
                if days_until_expiry <= 3:
                    priority = 'high'
                elif days_until_expiry <= 7:
                    priority = 'normal'
                else:
                    priority = 'low'
                
                user_items[item.user_id].append({
                    'id': item.id,
                    'name': item.name,
                    'days_until_expiry': days_until_expiry,
                    'expiry_date': item.expiry_date,
                    'priority': priority
                })
            
            # Send email notifications to each user
            for user_id, items in user_items.items():
                user = User.query.get(user_id)
                if user and user.email_notifications and user.email:
                    current_app.logger.info("Sending notification to user %s (%s) for %d items", 
                                          user.username, user.email, len(items))
                    self.send_daily_notification_email(user, items)
            
            current_app.logger.info("Completed expiry date check at %s", datetime.now())
            
        except Exception as e:
            current_app.logger.error(f"Error checking expiry dates: {str(e)}")
            raise
    
    def send_daily_notification_email(self, user: User, items: List[Dict[str, Any]]) -> bool:
        """Send a daily notification email to a user about their items.
        
        Args:
            user: The user to send the notification to
            items: List of items to notify about
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            if not items:
                current_app.logger.info("No items to notify about")
                return False
                
            # Sort items by days until expiry
            items.sort(key=lambda x: x['days_until_expiry'])
            
            # Prepare email content
            subject = "Expiry Tracker - Daily Item Status Update"
            template = 'daily_notification'
            
            # Send email
            result = self.email_service.send_email(
                subject=subject,
                recipients=[str(user.email)],  # Ensure email is converted to string
                template=template,
                user=user,
                items=items
            )
            
            if result:
                current_app.logger.info(f"Sent daily notification email to {user.email}")
                # Create notification record
                self.create_notification(
                    user_id=user.id,
                    item_id=items[0]['id'],  # Use first item's ID as reference
                    message=f"Daily status update sent for {len(items)} items",
                    type='email',
                    priority='normal'
                )
            else:
                current_app.logger.error(f"Failed to send daily notification email to {user.email}")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error sending daily notification email to {user.email}: {str(e)}")
            return False
    
    def create_notification(
        self,
        user_id: int,
        item_id: int,
        message: str,
        type: NotificationType,
        priority: NotificationPriority = 'normal',
        status: Literal['sent', 'pending'] = 'sent'
    ) -> Optional[Notification]:
        """Create a new notification record.
        
        Args:
            user_id: ID of the user to notify
            item_id: ID of the item this notification is about
            message: The notification message
            type: Type of notification (email)
            priority: Priority level of the notification
            status: Status of the notification (sent or pending)
            
        Returns:
            The created notification or None if creation failed
        """
        notification = Notification()
        notification.user_id = user_id
        notification.item_id = item_id
        notification.message = message
        notification.type = type
        notification.priority = priority
        notification.status = status
        
        try:
            db.session.add(notification)
            db.session.commit()
            return notification
        except Exception as e:
            current_app.logger.error(f"Error creating notification: {str(e)}")
            db.session.rollback()
            return None
    
    def get_user_notifications(self, user_id: int, limit: int = 10) -> List[Notification]:
        """Get notifications for a specific user.
        
        Args:
            user_id: The ID of the user to get notifications for
            limit: Maximum number of notifications to return
            
        Returns:
            List of Notification objects
        """
        try:
            notifications = Notification.query.filter_by(
                user_id=user_id,
                status='pending'  # Only get pending notifications
            ).filter(
                Notification.type.in_(['email'])
            ).order_by(
                Notification.created_at.desc()
            ).limit(limit).all()
            
            return notifications
        except Exception as e:
            current_app.logger.error(f"Error getting user notifications: {str(e)}")
            return [] 