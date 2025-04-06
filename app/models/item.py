from datetime import datetime
from app.core.extensions import db
from app.models.base import BaseModel
from flask import current_app
from functools import lru_cache
from typing import Optional, Union

# Status constants
STATUS_ACTIVE = 'Active'
STATUS_EXPIRED = 'Expired'
STATUS_EXPIRING_SOON = 'Expiring Soon'
STATUS_PENDING = 'Pending Expiry Date'

# Time constants
EXPIRING_SOON_DAYS = 30
PENDING_STATUS_HOURS = 24

class Item(BaseModel):
    """Item model for inventory management.
    
    This model represents an inventory item with its properties and status.
    It includes functionality for:
    - Tracking expiry dates and status
    - Managing prices (cost, selling, discounted)
    - Syncing with Zoho Inventory
    - Validating data integrity
    
    Attributes:
        name (str): Name of the item
        description (str): Optional description
        quantity (float): Current quantity in stock
        unit (str): Unit of measurement
        batch_number (str): Optional batch number
        purchase_date (datetime): Date of purchase
        expiry_date (datetime): Expiry date
        purchase_price (float): Original purchase price
        selling_price (float): Current selling price
        cost_price (float): Cost price for inventory valuation
        discounted_price (float): Optional discounted price
        location (str): Storage location
        notes (str): Additional notes
        image_url (str): Optional URL to item image
        status (str): Current status (Active/Expired/Expiring Soon/Pending)
        zoho_item_id (str): Unique identifier in Zoho Inventory
    """
    
    __tablename__ = 'items'
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(20))
    batch_number = db.Column(db.String(50))
    purchase_date = db.Column(db.DateTime)
    expiry_date = db.Column(db.DateTime)
    purchase_price = db.Column(db.Float)
    selling_price = db.Column(db.Float)
    cost_price = db.Column(db.Float)
    discounted_price = db.Column(db.Float)
    location = db.Column(db.String(100))
    notes = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    status_changed_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Pending Expiry Date')
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    zoho_item_id = db.Column(db.String(100), unique=True)
    
    # Relationships
    notifications = db.relationship('Notification', back_populates='item', lazy='dynamic')
    user = db.relationship('User', back_populates='items')
    
    @property
    def days_until_expiry(self) -> Optional[int]:
        """Calculate days until expiry with caching."""
        if not self.expiry_date:
            return None
        current_date = datetime.now().date()
        expiry_date = self.expiry_date.date() if isinstance(self.expiry_date, datetime) else self.expiry_date
        return (expiry_date - current_date).days
    
    @property
    def is_expired(self) -> bool:
        """Check if item is expired with caching."""
        days = self.days_until_expiry
        return days is not None and days <= 0
    
    @property
    def is_near_expiry(self) -> bool:
        """Check if item is near expiry with caching."""
        days = self.days_until_expiry
        return days is not None and 0 < days <= EXPIRING_SOON_DAYS
    
    def set_discount(self, percentage):
        """Set discounted price based on percentage."""
        if not self.selling_price:
            return
        self.discounted_price = self.selling_price * (1 - percentage / 100)
    
    def to_dict(self):
        """Convert item to dictionary."""
        current_date = datetime.now().date()
        days_until_expiry = None
        status = 'Unknown'

        if self.expiry_date:
            # Convert expiry_date to date if it's a datetime
            expiry_date = self.expiry_date.date() if isinstance(self.expiry_date, datetime) else self.expiry_date
            if expiry_date <= current_date:
                status = STATUS_EXPIRED
            else:
                days_until_expiry = (expiry_date - current_date).days
                if days_until_expiry <= EXPIRING_SOON_DAYS:
                    status = STATUS_EXPIRING_SOON
                else:
                    status = STATUS_ACTIVE
        elif self.status_changed_at:
            # If no expiry date but status changed within last 24 hours
            hours_since_change = (datetime.now() - self.status_changed_at).total_seconds() / 3600
            if hours_since_change <= PENDING_STATUS_HOURS:
                status = STATUS_PENDING
            else:
                status = STATUS_EXPIRING_SOON
                days_until_expiry = EXPIRING_SOON_DAYS  # Default to 30 days after grace period

        data = super().to_dict()
        data.update({
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'unit': self.unit,
            'batch_number': self.batch_number,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'expiry_date': self.expiry_date.strftime('%Y-%m-%d') if self.expiry_date else None,
            'purchase_price': self.purchase_price,
            'selling_price': self.selling_price,
            'cost_price': self.cost_price,
            'discounted_price': self.discounted_price,
            'location': self.location,
            'notes': self.notes,
            'image_url': self.image_url,
            'days_until_expiry': days_until_expiry,
            'is_expired': self.is_expired,
            'is_near_expiry': self.is_near_expiry,
            'status': status,
            'zoho_item_id': self.zoho_item_id
        })
        return data
    
    def __repr__(self):
        """String representation of the item."""
        return f'<Item {self.name}>'
    
    def validate_quantity(self):
        """Validate quantity is non-negative."""
        if self.quantity is not None and self.quantity < 0:
            raise ValueError("Quantity cannot be negative")
    
    def validate_prices(self):
        """Validate price relationships."""
        if self.cost_price is not None and self.cost_price < 0:
            raise ValueError("Cost price cannot be negative")
        if self.selling_price is not None and self.selling_price < 0:
            raise ValueError("Selling price cannot be negative")
        if self.purchase_price is not None and self.purchase_price < 0:
            raise ValueError("Purchase price cannot be negative")
    
    def validate_dates(self):
        """Validate date relationships."""
        if self.purchase_date and self.expiry_date:
            if self.purchase_date > self.expiry_date:
                raise ValueError("Purchase date cannot be after expiry date")
    
    def validate(self):
        """Run all validations."""
        self.validate_quantity()
        self.validate_prices()
        self.validate_dates()
        
    def save(self):
        """Save with validation."""
        self.validate()
        db.session.add(self)
        db.session.commit()
    
    def update_status(self, force_update: bool = False) -> None:
        """Update item status based on expiry date with optimized database calls."""
        if not self.expiry_date:
            self.status = STATUS_PENDING
            return

        old_status = self.status
        days_until_expiry = self.days_until_expiry

        # Calculate new status
        if days_until_expiry is None or days_until_expiry <= 0:
            new_status = STATUS_EXPIRED
        elif days_until_expiry <= EXPIRING_SOON_DAYS:
            new_status = STATUS_EXPIRING_SOON
        else:
            new_status = STATUS_ACTIVE

        # Update status if changed or forced
        if force_update or new_status != old_status:
            self.status = new_status
            self.status_changed_at = datetime.now()
            current_app.logger.info(
                f"Item {self.id} ({self.name}) status changed from {old_status} to {new_status}. "
                f"Days until expiry: {days_until_expiry}"
            )
            
            # Create notification for status change
            from app.services.notification_service import NotificationService
            notification_service = NotificationService()
            
            if new_status == STATUS_EXPIRED:
                notification_service.create_notification(
                    user_id=self.user_id,
                    item_id=self.id,
                    message=f"Item '{self.name}' has expired",
                    type='expiry',
                    priority='high'
                )
            elif new_status == STATUS_EXPIRING_SOON:
                notification_service.create_notification(
                    user_id=self.user_id,
                    item_id=self.id,
                    message=f"Item '{self.name}' is expiring in {days_until_expiry} days",
                    type='expiry',
                    priority='medium'
                )
            
            # Update Zoho status if synced
            if self.zoho_item_id:
                from app.services.zoho_service import ZohoService
                from app.models.user import User
                user = User.query.get(self.user_id)
                if user:
                    zoho_service = ZohoService(user)
                    zoho_status = 'active' if new_status in [STATUS_ACTIVE, STATUS_EXPIRING_SOON] else 'inactive'
                    zoho_service.update_item_status_in_zoho(self.zoho_item_id, zoho_status)
            
            db.session.commit() 