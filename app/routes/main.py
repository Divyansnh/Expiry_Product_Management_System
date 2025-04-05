from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.core.extensions import db
from app.models.item import Item
from app.services.notification_service import NotificationService
from app.services.zoho_service import ZohoService
from datetime import datetime, timedelta
from flask import session
from app.models.user import User
import secrets

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    with current_app.app_context():
        notification_service = NotificationService()
        
        # Get user's inventory items
        items = Item.query.filter_by(user_id=current_user.id).all()
        current_app.logger.info(f"Found {len(items)} total items for user {current_user.id}")
        
        # Update status for all items
        for item in items:
            item.update_status()
            current_app.logger.info(f"Item {item.name} (ID: {item.id}): status={item.status}, expiry_date={item.expiry_date}, days_until_expiry={item.days_until_expiry}")
        
        # Get expiring and expired items using model properties
        expiring_items = [item for item in items if item.is_near_expiry]
        expired_items = [item for item in items if item.is_expired]
        
        current_app.logger.info(f"Dashboard counts - Expiring: {len(expiring_items)}, Expired: {len(expired_items)}")
        for item in expiring_items:
            current_app.logger.info(f"Expiring item: {item.name} (ID: {item.id}), days until expiry: {item.days_until_expiry}")
        for item in expired_items:
            current_app.logger.info(f"Expired item: {item.name} (ID: {item.id}), days until expiry: {item.days_until_expiry}")
        
        # Get recent notifications
        notifications = notification_service.get_user_notifications(current_user.id, limit=5)
        
        return render_template('dashboard.html',
                             items=items,
                             expiring_items=expiring_items,
                             expired_items=expired_items,
                             notifications=notifications)

@main_bp.route('/inventory')
@login_required
def inventory():
    """Inventory management page."""
    zoho_service = ZohoService(current_user)
    
    # Check if connected to Zoho
    if not current_user.zoho_access_token:
        flash('Please connect to Zoho in Settings to sync your inventory.', 'warning')
        return render_template('inventory.html', items=[], current_status=None, current_search='', today_date=datetime.now().date().strftime('%Y-%m-%d'))
    
    # Try to refresh token if needed
    if current_user.zoho_token_expires_at and datetime.now() >= current_user.zoho_token_expires_at:
        if not zoho_service.refresh_token():
            flash('Failed to refresh Zoho connection. Please reconnect in Settings.', 'error')
            return render_template('inventory.html', items=[], current_status=None, current_search='', today_date=datetime.now().date().strftime('%Y-%m-%d'))
    
    # Try to sync with Zoho
    sync_success = zoho_service.sync_inventory(current_user)
    if not sync_success:
        flash('Failed to sync with Zoho inventory. Please check your connection in Settings.', 'error')
    
    # Update status for all items based on expiry date
    items = Item.query.filter_by(user_id=current_user.id).all()
    current_app.logger.info(f"Found {len(items)} total items for user {current_user.id}")
    
    for item in items:
        item.update_status()
        current_app.logger.info(f"Item {item.name} (ID: {item.id}): status={item.status}, expiry_date={item.expiry_date}, days_until_expiry={item.days_until_expiry}")
    
    # Get filter parameters
    status = request.args.get('status')
    search = request.args.get('search', '').strip()
    
    # Build query
    query = Item.query.filter_by(user_id=current_user.id)
    
    # Apply status filter
    if status:
        if status == 'expiring_soon':
            # Items expiring within 30 days but not expired
            query = query.filter(
                Item.expiry_date.isnot(None),
                Item.expiry_date > datetime.now().date(),
                Item.expiry_date <= (datetime.now().date() + timedelta(days=30))
            )
            current_app.logger.info("Filtering for expiring soon items")
        elif status == 'expired':
            # Items that have passed their expiry date
            query = query.filter(
                Item.expiry_date.isnot(None),
                Item.expiry_date <= datetime.now().date()
            )
            current_app.logger.info("Filtering for expired items")
        elif status == 'active':
            # Items that are not expired and not expiring soon
            query = query.filter(
                Item.expiry_date.isnot(None),
                Item.expiry_date > (datetime.now().date() + timedelta(days=30))
            )
            current_app.logger.info("Filtering for active items")
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Item.name.ilike(search_term),
                Item.description.ilike(search_term),
                Item.unit.ilike(search_term)
            )
        )
    
    items = query.all()
    current_app.logger.info(f"Inventory view counts - Total: {len(items)}, Status filter: {status}")
    
    # Update status for all items based on expiry date
    for item in items:
        item.update_status()
    
    # Log items by status
    expired_count = len([item for item in items if item.status == 'Expired'])
    expiring_count = len([item for item in items if item.status == 'Expiring Soon'])
    current_app.logger.info(f"Inventory status counts - Expired: {expired_count}, Expiring Soon: {expiring_count}")
    
    # Get Zoho status for each item
    for item in items:
        if item.zoho_item_id:
            item.zoho_status = zoho_service.get_item_status(item.zoho_item_id)
        else:
            item.zoho_status = None
    
    return render_template('inventory.html',
                         items=items,
                         current_status=status,
                         current_search=search,
                         today_date=datetime.now().date().strftime('%Y-%m-%d'))

@main_bp.route('/notifications')
@login_required
def notifications():
    """Notifications page."""
    notification_service = NotificationService()
    notifications = notification_service.get_user_notifications(current_user.id)
    return render_template('notifications.html', notifications=notifications)

@main_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    notification_service = NotificationService()
    success = notification_service.mark_notification_read(notification_id, current_user.id)
    
    if success:
        flash('Notification marked as read', 'success')
    else:
        flash('Notification not found', 'error')
    
    return redirect(url_for('main.notifications'))

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page."""
    if request.method == 'POST':
        try:
            # Update username
            new_username = request.form.get('username')
            if new_username and new_username != current_user.username:
                if User.query.filter_by(username=new_username).first():
                    flash('Username already exists', 'error')
                    return redirect(url_for('main.settings'))
                current_user.username = new_username
            
            # Update email
            new_email = request.form.get('email')
            if new_email and new_email != current_user.email:
                if User.query.filter_by(email=new_email).first():
                    flash('Email already exists', 'error')
                    return redirect(url_for('main.settings'))
                current_user.email = new_email
            
            # Update password if provided
            new_password = request.form.get('new_password')
            if new_password:
                confirm_password = request.form.get('confirm_password')
                if new_password != confirm_password:
                    flash('Passwords do not match', 'error')
                    return redirect(url_for('main.settings'))
                try:
                    current_user.password = new_password  # This will validate password strength
                except ValueError as e:
                    flash(str(e), 'error')
                    return redirect(url_for('main.settings'))
            
            # Update Zoho credentials if provided
            new_zoho_client_id = request.form.get('zoho_client_id')
            new_zoho_client_secret = request.form.get('zoho_client_secret')
            
            if new_zoho_client_id or new_zoho_client_secret:
                # Check for duplicate credentials
                existing_user = User.query.filter(
                    User.zoho_client_id == new_zoho_client_id,
                    User.zoho_client_secret == new_zoho_client_secret,
                    User.id != current_user.id
                ).first()
                
                if existing_user:
                    flash('These Zoho credentials are already in use by another user. Please use different credentials.', 'error')
                    return redirect(url_for('main.settings'))
                
                # If no duplicates found, update the credentials
                if new_zoho_client_id:
                    current_user.zoho_client_id = new_zoho_client_id
                if new_zoho_client_secret:
                    current_user.zoho_client_secret = new_zoho_client_secret
            
            db.session.commit()
            flash('Account settings updated successfully!', 'success')
            return redirect(url_for('main.settings'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating settings: {str(e)}")
            flash('An error occurred while updating settings', 'error')
            return redirect(url_for('main.settings'))
    
    return render_template('settings.html')

@main_bp.route('/settings/notifications', methods=['POST'])
@login_required
def update_notification_settings():
    """Update notification preferences."""
    try:
        current_user.email_notifications = request.form.get('email_notifications') == 'on'
        current_user.sms_notifications = request.form.get('sms_notifications') == 'on'
        current_user.in_app_notifications = request.form.get('in_app_notifications') == 'on'
        current_user.save()
        
        flash('Notification settings updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating notification settings: {str(e)}', 'error')
    
    return redirect(url_for('main.settings'))

@main_bp.route('/help')
def help():
    """Help and documentation page."""
    return render_template('help.html')

@main_bp.route('/contact')
def contact():
    """Contact page."""
    return render_template('contact.html')

@main_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')

@main_bp.route('/api/v1/items', methods=['POST'])
@login_required
def add_item():
    """Add a new item to inventory."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate required fields
        required_fields = ['name', 'quantity', 'unit', 'cost_price', 'selling_price', 'expiry_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create item in Zoho first
        zoho_service = ZohoService(current_user)
        zoho_item = zoho_service.create_item_in_zoho(data)
        
        if not zoho_item:
            return jsonify({'error': 'Failed to create item in Zoho'}), 500
            
        # Create local item
        item = Item(
            user_id=current_user.id,
            zoho_item_id=str(zoho_item['item_id']),
            name=data['name'],
            description=data.get('description', ''),
            quantity=float(data['quantity']),
            unit=data['unit'],
            selling_price=float(data['selling_price']),
            cost_price=float(data['cost_price']),
            expiry_date=datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'message': 'Item added successfully',
            'item': {
                'id': item.id,
                'name': item.name,
                'quantity': item.quantity,
                'unit': item.unit,
                'expiry_date': item.expiry_date.strftime('%Y-%m-%d')
            }
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error adding item: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/update_item/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    """Update an existing item."""
    try:
        item = Item.query.get_or_404(item_id)
        if item.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Update item in local database
        item.name = data.get('name', item.name)
        
        # Handle numeric fields with None checks
        if 'quantity' in data:
            item.quantity = float(data['quantity']) if data['quantity'] is not None else 0.0
        if 'selling_price' in data:
            item.selling_price = float(data['selling_price']) if data['selling_price'] is not None else None
        if 'cost_price' in data:
            item.cost_price = float(data['cost_price']) if data['cost_price'] is not None else None
        if 'discounted_price' in data:
            item.discounted_price = float(data['discounted_price']) if data['discounted_price'] is not None else None
            
        item.unit = data.get('unit', item.unit)
        item.description = data.get('description', item.description)
        if 'expiry_date' in data:
            # Convert string to date object
            item.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        
        db.session.commit()
        
        # Sync with Zoho if connected and item has a Zoho ID
        if current_user.zoho_access_token and item.zoho_item_id:
            zoho_service = ZohoService(current_user)
            # Convert date to string for Zoho API
            item_data = item.to_dict()
            if item.expiry_date:
                item_data['expiry_date'] = item.expiry_date.strftime('%Y-%m-%d')
            
            if zoho_service.update_item_in_zoho(item.zoho_item_id, item_data):
                current_app.logger.info(f"Successfully synced item {item.id} with Zoho")
                flash('Item updated successfully and synced with Zoho', 'success')
            else:
                current_app.logger.warning(f"Failed to sync item {item.id} with Zoho")
                flash('Item updated locally but failed to sync with Zoho', 'warning')
        else:
            current_app.logger.info(f"Successfully updated item {item.id} locally")
            flash('Item updated successfully', 'success')
        
        return jsonify({'success': True, 'item': item.to_dict()})
        
    except ValueError as e:
        db.session.rollback()
        current_app.logger.error(f"Invalid data format: {str(e)}")
        return jsonify({'success': False, 'error': 'Invalid data format'}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating item: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/delete_item/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """Delete an item."""
    try:
        item = Item.query.get_or_404(item_id)
        
        # Check if user owns the item
        if item.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # If connected to Zoho and item has a Zoho ID, mark it as inactive in Zoho
        if current_user.zoho_access_token and item.zoho_item_id:
            zoho_service = ZohoService(current_user)
            if not zoho_service.delete_item_in_zoho(item.zoho_item_id):
                current_app.logger.error(f"Failed to mark item {item.id} as inactive in Zoho")
                return jsonify({'success': False, 'error': 'Failed to delete item in Zoho'}), 500
        
        # Delete from local database
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item deleted successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error deleting item: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to delete item'}), 500

@main_bp.route('/get_item/<int:item_id>')
@login_required
def get_item(item_id):
    """Get item details for editing."""
    try:
        item = Item.query.get_or_404(item_id)
        if item.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
        # Get Zoho status if connected
        zoho_status = None
        if current_user.zoho_access_token and item.zoho_item_id:
            try:
                zoho_service = ZohoService(current_user)
                zoho_status = zoho_service.get_item_status(item.zoho_item_id)
            except Exception as e:
                current_app.logger.warning(f"Could not get Zoho status for item {item_id}: {str(e)}")
                zoho_status = None
            
        return jsonify({
            'success': True,
            'item': {
                'id': item.id,
                'name': item.name,
                'quantity': item.quantity,
                'unit': item.unit,
                'selling_price': item.selling_price,
                'cost_price': item.cost_price,
                'description': item.description,
                'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None,
                'status': item.status,
                'zoho_status': zoho_status
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error getting item details: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/settings/zoho-credentials', methods=['POST'])
@login_required
def update_zoho_credentials():
    """Update user's Zoho client credentials."""
    try:
        new_zoho_client_id = request.form.get('zoho_client_id')
        new_zoho_client_secret = request.form.get('zoho_client_secret')
        
        # Check for duplicate credentials
        existing_user = User.query.filter(
            User.zoho_client_id == new_zoho_client_id,
            User.zoho_client_secret == new_zoho_client_secret,
            User.id != current_user.id
        ).first()
        
        if existing_user:
            flash('These Zoho credentials are already in use by another user. Please use different credentials.', 'error')
            return redirect(url_for('main.settings'))
        
        # If no duplicates found, update the credentials
        current_user.zoho_client_id = new_zoho_client_id
        current_user.zoho_client_secret = new_zoho_client_secret
        db.session.commit()
        
        flash('Zoho credentials updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating Zoho credentials: {str(e)}")
        flash('An error occurred while updating Zoho credentials', 'error')
    
    return redirect(url_for('main.settings'))

@main_bp.route('/api/v1/items/bulk-delete', methods=['POST'])
@login_required
def bulk_delete_items():
    """Delete multiple items at once."""
    try:
        data = request.get_json()
        if not data or 'item_ids' not in data:
            return jsonify({'error': 'No item IDs provided'}), 400
            
        item_ids = data['item_ids']
        if not isinstance(item_ids, list):
            return jsonify({'error': 'Item IDs must be a list'}), 400
            
        if len(item_ids) > 20:
            return jsonify({'error': 'Cannot delete more than 20 items at once'}), 400
            
        # Get all items that belong to the current user
        items = Item.query.filter(
            Item.id.in_(item_ids),
            Item.user_id == current_user.id
        ).all()
        
        if not items:
            return jsonify({'error': 'No valid items found'}), 404
            
        # If connected to Zoho, mark items as inactive
        if current_user.zoho_access_token:
            zoho_service = ZohoService(current_user)
            for item in items:
                if item.zoho_item_id:
                    zoho_service.delete_item_in_zoho(item.zoho_item_id)
        
        # Delete items from database
        for item in items:
            db.session.delete(item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted {len(items)} items'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in bulk delete: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/save-zoho-credentials', methods=['POST'])
def save_zoho_credentials():
    if not current_user.is_authenticated:
        flash('Please log in to connect your Zoho account', 'warning')
        return redirect(url_for('auth.login'))
        
    form = ZohoCredentialsForm()
    if form.validate_on_submit():
        try:
            # Store the credentials in the session temporarily
            session['zoho_credentials'] = {
                'client_id': form.client_id.data,
                'client_secret': form.client_secret.data,
                'organization_id': form.organization_id.data
            }
            
            # Generate state parameter for security
            state = secrets.token_urlsafe(16)
            session['oauth_state'] = state
            
            # Redirect to Zoho authorization URL
            auth_url = zoho_service.get_authorization_url(state)
            return redirect(auth_url)
            
        except Exception as e:
            current_app.logger.error(f"Error preparing Zoho authorization: {str(e)}")
            flash('An error occurred while preparing Zoho authorization', 'error')
            return redirect(url_for('main.settings'))
            
    flash('Invalid form submission', 'error')
    return redirect(url_for('main.settings')) 