from datetime import datetime
from app.core.extensions import db
from app.models.base import BaseModel

class Notification(BaseModel):
    """Model for storing user notifications."""
    
    __tablename__ = 'notifications'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(10), default='medium')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    user = db.relationship('User', back_populates='notifications')
    item = db.relationship('Item', back_populates='notifications')
    
    def to_dict(self) -> dict:
        """Convert notification to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'item_id': self.item_id,
            'message': self.message,
            'type': self.type,
            'priority': self.priority,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.message}>' 