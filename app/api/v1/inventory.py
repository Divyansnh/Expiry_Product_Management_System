from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_bp
from app.core.extensions import db
from app.models.item import Item
from app.models.user import User
from app.services.zoho_service import ZohoService
from app.services.notification_service import NotificationService
from datetime import datetime
from typing import List, Dict, Any, Optional

@api_bp.route('/inventory', methods=['GET'])
@jwt_required()
def get_inventory():
    """Get user's inventory items."""
    user_id = get_jwt_identity()
    user: Optional[User] = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    items = Item.query.filter_by(user_id=user_id).all()
    
    # Update status for all items
    for item in items:
        item.update_status(force_update=True)
    
    return jsonify([item.to_dict() for item in items])

@api_bp.route('/inventory/bulk-delete', methods=['POST'])
@jwt_required()
def bulk_delete_items():
    """Delete multiple items."""
    user_id = get_jwt_identity()
    user: Optional[User] = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    item_ids = data.get('item_ids', [])
    
    if not item_ids:
        return jsonify({'error': 'No items selected'}), 400
    
    try:
        # Get items and verify ownership
        items = Item.query.filter(
            Item.id.in_(item_ids),
            Item.user_id == user_id
        ).all()
        
        if not items:
            return jsonify({'error': 'No valid items found'}), 404
        
        # Delete items from Zoho first
        zoho_service = ZohoService(user)
        for item in items:
            if item.zoho_item_id:
                zoho_service.delete_item_in_zoho(item.zoho_item_id)
        
        # Delete items from local database
        for item in items:
            db.session.delete(item)
        
        db.session.commit()
        return jsonify({'message': f'Successfully deleted {len(items)} items'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/inventory/sync', methods=['POST'])
@jwt_required()
def sync_inventory():
    """Sync inventory with Zoho."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    zoho_service = ZohoService()
    success = zoho_service.sync_inventory(user)
    if success:
        return jsonify({'message': 'Inventory synced successfully'})
    return jsonify({'error': 'Failed to sync inventory'}), 500

@api_bp.route('/inventory/<int:item_id>', methods=['GET'])
@jwt_required()
def get_item(item_id):
    """Get a specific inventory item."""
    user_id = get_jwt_identity()
    item = Item.query.filter_by(id=item_id, user_id=user_id).first()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    return jsonify(item.to_dict())

@api_bp.route('/inventory/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    """Update an item."""
    user_id = get_jwt_identity()
    user: Optional[User] = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    try:
        item = Item.query.filter_by(id=item_id, user_id=user_id).first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        # Update item fields
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        # Update status and sync with Zoho
        item.update_status(force_update=True)
        
        db.session.commit()
        return jsonify({'message': 'Item updated successfully', 'item': item.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/inventory/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    """Delete an inventory item."""
    user_id = get_jwt_identity()
    item = Item.query.filter_by(id=item_id, user_id=user_id).first()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    try:
        item.delete()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/inventory/expiring', methods=['GET'])
@jwt_required()
def get_expiring_items():
    """Get items that are expiring soon."""
    user_id = get_jwt_identity()
    items = Item.query.filter_by(user_id=user_id).all()
    expiring_items = [item for item in items if item.is_near_expiry]
    return jsonify([item.to_dict() for item in expiring_items])

@api_bp.route('/inventory/expired', methods=['GET'])
@jwt_required()
def get_expired_items():
    """Get expired items."""
    user_id = get_jwt_identity()
    items = Item.query.filter_by(user_id=user_id).all()
    expired_items = [item for item in items if item.is_expired]
    return jsonify([item.to_dict() for item in expired_items]) 