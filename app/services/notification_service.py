from datetime import datetime, timedelta
from typing import List, Optional, Union, Dict, Any, Literal, TypedDict, Sequence, cast
from flask import current_app
from app.core.extensions import db
from app.models.notification import Notification
from app.models.item import Item
from app.models.user import User
from app.services.email_service import EmailService

class ItemNotification(TypedDict):
    name: str
    days_until_expiry: int
    priority: Literal['high', 'normal', 'low']

class UserNotifications(TypedDict):
    expiring: List[ItemNotification]
    expired: List[ItemNotification]

NotificationType = Literal['in_app', 'email', 'sms']
NotificationPriority = Literal['high', 'normal', 'low']

class NotificationService:
    """Service for handling expiry notifications."""
    
    def __init__(self) -> None:
        self._notification_days: Optional[List[int]] = None
    
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
    
    def check_expiry_dates(self) -> List[Notification]:
        """Check items for expiry and create notifications."""
        notifications: List[Notification] = []
        today = datetime.utcnow()
        
        # Group notifications by user
        user_notifications: Dict[int, UserNotifications] = {}
        
        # Get all items with expiry dates
        items = Item.query.filter(
            Item.expiry_date.isnot(None),
            Item.expiry_date > today
        ).all()
        
        # Get recently expired items (expired in last 24 hours)
        recently_expired = Item.query.filter(
            Item.expiry_date.isnot(None),
            Item.expiry_date <= today,
            Item.expiry_date >= today - timedelta(days=1)
        ).all()
        
        # Handle recently expired items first
        for item in recently_expired:
            if item.user.email_notifications:
                if item.user_id not in user_notifications:
                    user_notifications[item.user_id] = {
                        'expiring': [],
                        'expired': []
                    }
                
                user_notifications[item.user_id]['expired'].append({
                    'name': item.name,
                    'days_until_expiry': 0,
                    'priority': 'high'
                })
        
        # Handle items approaching expiry
        for item in items:
            days_until_expiry = item.days_until_expiry
            if days_until_expiry is None:
                continue
                
            # Check if we need to send a notification
            if days_until_expiry in self.notification_days:
                # Only create in-app notification if user has enabled them
                if item.user.in_app_notifications:
                    notification = self._create_notification(item)
                    if notification:
                        notifications.append(notification)
                    
                # Group notification by user for email
                if item.user.email_notifications:
                    if item.user_id not in user_notifications:
                        user_notifications[item.user_id] = {
                            'expiring': [],
                            'expired': []
                        }
                    
                    user_notifications[item.user_id]['expiring'].append({
                        'name': item.name,
                        'days_until_expiry': days_until_expiry,
                        'priority': notification.priority if notification else 'normal'
                    })
        
        # Send batched email notifications
        for user_id, data in user_notifications.items():
            user = User.query.get(user_id)
            if user and self._should_send_email(user_id):
                # Combine expiring and expired items
                all_items = data['expired'] + data['expiring']
                # Sort items by priority (high -> normal -> low)
                all_items.sort(key=lambda x: {'high': 0, 'normal': 1, 'low': 2}[x['priority']])
                
                if all_items:  # Only send if there are items to notify about
                    # Convert ItemNotification to Dict for EmailService
                    items_dict = cast(List[Dict[str, Any]], all_items)
                    if EmailService.send_daily_notification_email(user, items_dict):
                        self._mark_email_sent(user_id)
        
        return notifications
    
    def _should_send_email(self, user_id: int) -> bool:
        """Check if we should send an email to this user."""
        # Get the last email notification for this user
        last_notification = Notification.query.filter_by(
            user_id=user_id,
            type='email',
            status='sent'
        ).order_by(Notification.created_at.desc()).first()
        
        if not last_notification:
            return True
            
        # Check if 24 hours have passed since the last email
        hours_since_last = (datetime.utcnow() - last_notification.created_at).total_seconds() / 3600
        return hours_since_last >= 24
    
    def _mark_email_sent(self, user_id: int) -> None:
        """Mark that an email was sent to this user."""
        notification = Notification()
        notification.message = "Daily expiry alert email sent"
        notification.type = 'email'
        notification.status = 'sent'
        notification.user_id = user_id
        
        db.session.add(notification)
        db.session.commit()
    
    def _create_notification(self, item: Item) -> Optional[Notification]:
        """Create a notification for an item."""
        days_until_expiry = item.days_until_expiry
        if days_until_expiry is None:
            return None
            
        # Determine priority based on days until expiry
        if days_until_expiry == 1:
            priority: NotificationPriority = 'high'
            message = f"Critical: Product {item.name} (ID: {item.id}) expires tomorrow!"
        elif days_until_expiry <= 3:
            priority = 'high'
            message = f"Warning: Product {item.name} (ID: {item.id}) expires in {days_until_expiry} days!"
        elif days_until_expiry <= 7:
            priority = 'normal'
            message = f"Notice: Product {item.name} (ID: {item.id}) expires in {days_until_expiry} days."
        else:
            priority = 'low'
            message = f"Info: Product {item.name} (ID: {item.id}) expires in {days_until_expiry} days."
        
        # Check if a similar notification already exists for today
        today = datetime.utcnow().date()
        existing = Notification.query.filter(
            Notification.item_id == item.id,
            Notification.type == 'in_app',
            Notification.status == 'pending',
            db.func.date(Notification.created_at) == today
        ).first()
        
        if existing:
            return None
        
        notification = Notification()
        notification.message = message
        notification.type = 'in_app'
        notification.priority = priority
        notification.user_id = item.user_id
        notification.item_id = item.id
        notification.status = 'pending'
        
        db.session.add(notification)
        db.session.commit()
        
        return notification
    
    def send_sms_notification(self, notification: Notification) -> bool:
        """Send SMS notification using Twilio."""
        if not current_app.config['TWILIO_ACCOUNT_SID']:
            return False
            
        try:
            from twilio.rest import Client
            
            client = Client(
                current_app.config['TWILIO_ACCOUNT_SID'],
                current_app.config['TWILIO_AUTH_TOKEN']
            )
            
            message = client.messages.create(
                body=notification.message,
                from_=current_app.config['TWILIO_PHONE_NUMBER'],
                to=notification.user.phone_number  # You'll need to add this to User model
            )
            
            if message.sid:
                notification.status = 'sent'
                db.session.commit()
                return True
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error sending SMS notification: {str(e)}")
            notification.status = 'failed'
            db.session.commit()
            return False
    
    def send_email_notification(self, notification: Notification) -> bool:
        """Send email notification."""
        # TODO: Implement email sending functionality
        # This would use Flask-Mail or similar
        return False
    
    def get_user_notifications(self, user_id: int, limit: Optional[int] = None) -> List[Notification]:
        """Get notifications for a user.
        
        Args:
            user_id: ID of the user
            limit: Optional limit on number of notifications to return
            
        Returns:
            List of notifications, optionally limited in number
        """
        # Get user preferences
        user = User.query.get(user_id)
        if not user or not user.in_app_notifications:
            return []
            
        query = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc())
        if limit is not None:
            query = query.limit(limit)
        return query.all()
    
    def mark_notification_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read."""
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()
        
        if notification:
            notification.status = 'read'
            db.session.commit()
            return True
        return False
    
    def create_notification(
        self,
        user_id: int,
        item_id: int,
        message: str,
        type: NotificationType,
        priority: NotificationPriority = 'normal'
    ) -> Optional[Notification]:
        """Create a new notification.
        
        Args:
            user_id: ID of the user to notify
            item_id: ID of the item this notification is about
            message: The notification message
            type: Type of notification (in_app, email, or sms)
            priority: Priority level of the notification
            
        Returns:
            The created notification or None if creation failed
        """
        notification = Notification()
        notification.user_id = user_id
        notification.item_id = item_id
        notification.message = message
        notification.type = type
        notification.priority = priority
        notification.status = 'pending'
        
        try:
            db.session.add(notification)
            db.session.commit()
            return notification
        except Exception as e:
            current_app.logger.error(f"Error creating notification: {str(e)}")
            db.session.rollback()
            return None
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Mark a notification as read."""
        notification = Notification.query.get(notification_id)
        if notification:
            notification.status = 'read'
            db.session.commit()
            return True
        return False 