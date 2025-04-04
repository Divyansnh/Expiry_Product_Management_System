import os
import time
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app, session, request
from flask_login import current_user
from app.core.extensions import db
from app.models.item import Item
from app.models.user import User
from urllib.parse import urlencode

class ZohoService:
    """Service for interacting with Zoho Inventory API."""
    
    def __init__(self, user: User):
        """Initialize service with user."""
        self.user = user
        self.client_id = user.zoho_client_id or current_app.config['ZOHO_CLIENT_ID']
        self.client_secret = user.zoho_client_secret or current_app.config['ZOHO_CLIENT_SECRET']
        self.redirect_uri = current_app.config['ZOHO_REDIRECT_URI']
        self.base_url = current_app.config['ZOHO_API_BASE_URL']
        self.accounts_url = current_app.config['ZOHO_ACCOUNTS_URL']
    
    def get_access_token(self) -> Optional[str]:
        """Get the current access token from user record."""
        if not self.user:
            current_app.logger.error("No user available")
            return None
            
        # Check if token exists and is not expired
        if self.user.zoho_access_token and self.user.zoho_token_expires_at:
            if datetime.now() >= self.user.zoho_token_expires_at:
                current_app.logger.info("Access token expired, attempting to refresh")
                if self.refresh_token():
                    return self.user.zoho_access_token
                return None
            return self.user.zoho_access_token
            
        current_app.logger.error("No access token available")
        return None
    
    def get_refresh_token(self) -> Optional[str]:
        """Get the refresh token from user record."""
        return self.user.zoho_refresh_token if self.user else None
    
    def refresh_token(self) -> bool:
        """Refresh the access token using the refresh token."""
        refresh_token = self.get_refresh_token()
        if not refresh_token:
            current_app.logger.error("No refresh token available")
            return False
        
        try:
            response = requests.post(
                f"{self.accounts_url}/oauth/v2/token",
                data={
                    'refresh_token': refresh_token,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'refresh_token'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' not in data:
                    current_app.logger.error(f"Invalid refresh token response: {data}")
                    return False
                    
                self.user.zoho_access_token = data['access_token']
                self.user.zoho_token_expires_at = datetime.now() + timedelta(seconds=data.get('expires_in', 3600))
                db.session.commit()
                current_app.logger.info("Successfully refreshed access token")
                return True
                
            current_app.logger.error(f"Failed to refresh token: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error refreshing Zoho token: {str(e)}")
            return False
    
    def get_inventory(self) -> Optional[List[Dict[str, Any]]]:
        """Get inventory data from Zoho."""
        access_token = self.get_access_token()
        if not access_token:
            current_app.logger.error("No access token available")
            return None
            
        try:
            current_app.logger.info("Fetching inventory data from Zoho")
            
            # Get items
            response = requests.get(
                f"{self.base_url}/items",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                params={
                    'status': 'active'
                }
            )
            
            if response.status_code == 401:
                current_app.logger.error("Unauthorized - token may be invalid")
                return None
                
            if response.status_code != 200:
                current_app.logger.error(f"Failed to get inventory: {response.status_code} - {response.text}")
                return None
                
            try:
                data = response.json()
                if not isinstance(data, dict) or 'items' not in data:
                    current_app.logger.error(f"Invalid response format: {data}")
                    return None
                    
                current_app.logger.info(f"Successfully fetched {len(data['items'])} items from Zoho")
                return data['items']
                
            except json.JSONDecodeError as e:
                current_app.logger.error(f"Failed to parse inventory response: {response.text}")
                return None
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error making API request: {str(e)}")
            return None
        except Exception as e:
            current_app.logger.error(f"Unexpected error: {str(e)}")
            return None
    
    def sync_inventory(self, user: User) -> bool:
        """Sync inventory with Zoho"""
        try:
            # Get access token
            access_token = self.get_access_token()
            if not access_token:
                current_app.logger.error("No access token available")
                return False

            # Fetch inventory data from Zoho
            current_app.logger.info("Fetching inventory data from Zoho")
            response = requests.get(
                f"{self.base_url}/items",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                params={
                    'status': 'active'
                }
            )
            
            if response.status_code == 401:
                current_app.logger.error("Unauthorized - token may be invalid")
                return False
                
            if response.status_code != 200:
                current_app.logger.error(f"Failed to fetch inventory: {response.status_code} - {response.text}")
                return False
            
            try:
                data = response.json()
                if not isinstance(data, dict) or 'items' not in data:
                    current_app.logger.error(f"Invalid response format: {data}")
                    return False
                    
                items = data['items']
                current_app.logger.info(f"Successfully fetched {len(items)} active items from Zoho")
            except json.JSONDecodeError as e:
                current_app.logger.error(f"Failed to parse inventory response: {response.text}")
                return False
            
            # Get existing items for this user
            existing_items = Item.query.filter_by(user_id=user.id).all()
            existing_item_map = {item.zoho_item_id: item for item in existing_items}
            
            # Track processed items to identify items to deactivate
            processed_zoho_ids = set()
            
            for item_data in items:
                try:
                    # Extract item details
                    zoho_item_id = str(item_data.get('item_id'))
                    name = item_data.get('name', '')
                    description = item_data.get('description', '')
                    unit = item_data.get('unit', '')
                    rate = float(item_data.get('rate', 0))
                    purchase_rate = float(item_data.get('purchase_rate', 0))
                    stock_on_hand = float(item_data.get('stock_on_hand', 0))
                    status = item_data.get('status', 'active')
                    
                    # Create or update item
                    item = existing_item_map.get(zoho_item_id)
                    if not item:
                        item = Item()
                        item.user_id = user.id
                        item.zoho_item_id = zoho_item_id
                        item.name = name
                        item.description = description
                        item.unit = unit
                        item.selling_price = rate
                        item.cost_price = purchase_rate
                        item.quantity = stock_on_hand
                        item.status = status
                        db.session.add(item)
                    else:
                        # Update existing item
                        item.name = name
                        item.description = description
                        item.unit = unit
                        item.selling_price = rate
                        item.cost_price = purchase_rate
                        item.quantity = stock_on_hand
                        item.status = status
                    
                    processed_zoho_ids.add(zoho_item_id)
                    
                except Exception as e:
                    current_app.logger.error(f"Error processing item {zoho_item_id}: {str(e)}")
                    continue
            
            # Mark items not in Zoho as inactive
            for item in existing_items:
                if item.zoho_item_id not in processed_zoho_ids:
                    item.status = 'inactive'
            
            db.session.commit()
            current_app.logger.info(f"Successfully synced inventory for user {user.id}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error syncing inventory: {str(e)}")
            db.session.rollback()
            return False
    
    def get_auth_url(self) -> str:
        """Get the Zoho OAuth authorization URL."""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'ZohoInventory.FullAccess.all',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        current_app.logger.info(f"Generating auth URL with params: {params}")
        auth_url = f"{self.accounts_url}/oauth/v2/auth"
        query_string = urlencode(params)
        full_url = f"{auth_url}?{query_string}"
        current_app.logger.info(f"Generated auth URL: {full_url}")
        return full_url
    
    def handle_callback(self, code: str) -> bool:
        """Handle the OAuth callback and store tokens."""
        try:
            # Exchange code for tokens
            token_url = f"{self.accounts_url}/oauth/v2/token"
            current_app.logger.info(f"Requesting token from: {token_url}")
            
            data = {
                'code': code,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri,
                'grant_type': 'authorization_code',
                'access_type': 'offline'
            }
            
            current_app.logger.info(f"Token request data: {data}")
            response = requests.post(token_url, data=data)
            
            if response.status_code != 200:
                current_app.logger.error(f"Failed to get token: {response.status_code} - {response.text}")
                return False
                
            try:
                token_data = response.json()
                current_app.logger.info(f"Received token response: {token_data}")
            except json.JSONDecodeError as e:
                current_app.logger.error(f"Failed to parse token response: {response.text}")
                return False
            
            # Check if we got all required tokens
            if 'access_token' not in token_data or 'refresh_token' not in token_data:
                current_app.logger.error(f"Missing required tokens in response: {token_data}")
                return False
                
            # Store tokens in user's database record
            self.user.zoho_access_token = token_data['access_token']
            self.user.zoho_refresh_token = token_data['refresh_token']
            self.user.zoho_token_expires_at = datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
            
            # Commit token changes first
            db.session.commit()
            current_app.logger.info(f"Successfully stored tokens for user {self.user.id}")
            
            # Try to get organization ID, but don't fail if we can't
            try:
                org_response = requests.get(
                    f"{self.base_url}/organizations",
                    headers={
                        'Authorization': f'Bearer {token_data["access_token"]}',
                        'Content-Type': 'application/json'
                    }
                )
                
                if org_response.status_code == 200:
                    try:
                        org_data = org_response.json()
                        current_app.logger.info(f"Organization response: {org_data}")
                        if org_data.get('organizations'):
                            self.user.zoho_organization_id = org_data['organizations'][0]['organization_id']
                            db.session.commit()
                            current_app.logger.info(f"Successfully stored organization ID for user {self.user.id}")
                    except json.JSONDecodeError as e:
                        current_app.logger.error(f"Failed to parse organization response: {org_response.text}")
                else:
                    current_app.logger.error(f"Failed to get organization ID: {org_response.status_code} - {org_response.text}")
            except Exception as e:
                current_app.logger.error(f"Error getting organization ID: {str(e)}")
                # Don't fail the whole process if we can't get the organization ID
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error handling callback: {str(e)}")
            db.session.rollback()
            return False

    def get_item_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get an item from Zoho by name."""
        access_token = self.get_access_token()
        if not access_token:
            current_app.logger.error("No access token available")
            return None
            
        try:
            # First try to find active items
            response = requests.get(
                f"{self.base_url}/items",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                params={
                    'name': name,
                    'status': 'active'  # Check active items first
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                if items:
                    current_app.logger.info(f"Found active item with name '{name}' in Zoho")
                    return items[0]
            
            # If no active items found, check inactive items
            response = requests.get(
                f"{self.base_url}/items",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                params={
                    'name': name,
                    'status': 'inactive'  # Check inactive items
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                if items:
                    current_app.logger.info(f"Found inactive item with name '{name}' in Zoho")
                    return items[0]
            
            current_app.logger.info(f"No items found with name '{name}' in Zoho")
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error getting item from Zoho: {str(e)}")
            return None

    def create_item_in_zoho(self, item_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new item in Zoho Inventory."""
        access_token = self.get_access_token()
        if not access_token:
            current_app.logger.error("No access token available")
            return None
            
        try:
            current_app.logger.info(f"Creating item in Zoho with status: {item_data.get('status', 'active')}")
            
            # Check if item already exists in Zoho (both active and inactive)
            existing_item = self.get_item_by_name(item_data['name'])
            if existing_item:
                if existing_item.get('status') == 'inactive':
                    current_app.logger.info(f"Found inactive item '{item_data['name']}' in Zoho. Reactivating it.")
                    # Reactivate the item
                    response = requests.put(
                        f"{self.base_url}/items/{existing_item['item_id']}",
                        headers={
                            'Authorization': f'Bearer {access_token}',
                            'Content-Type': 'application/json'
                        },
                        json={
                            "status": "active",
                            "name": item_data['name'],
                            "unit": item_data['unit'],
                            "rate": float(item_data['selling_price']),
                            "description": item_data.get('description', ''),
                            "stock_on_hand": float(item_data['quantity'])
                        }
                    )
                    
                    if response.status_code == 200:
                        current_app.logger.info(f"Successfully reactivated item in Zoho: {existing_item['item_id']}")
                        return existing_item
                    else:
                        current_app.logger.error(f"Failed to reactivate item in Zoho: {response.status_code} - {response.text}")
                else:
                    current_app.logger.info(f"Item '{item_data['name']}' already exists in Zoho. Linking to existing item.")
                    return existing_item
            
            # Determine status based on expiry date
            expiry_date = datetime.strptime(item_data['expiry_date'], '%Y-%m-%d').date()
            current_date = datetime.now().date()
            status = "inactive" if expiry_date <= current_date else "active"
            
            # Create item with only essential fields
            request_data = {
                "name": item_data['name'],
                "unit": item_data['unit'],
                "rate": float(item_data['selling_price']),
                "description": item_data.get('description', ''),
                "status": status,
                "item_type": "inventory",
                "product_type": "goods"
            }
            
            # Add stock information
            if item_data.get('quantity'):
                request_data["initial_stock"] = float(item_data['quantity'])
                if item_data.get('cost_price'):
                    request_data["initial_stock_rate"] = float(item_data['cost_price'])
            
            current_app.logger.info(f"Creating item in Zoho with data: {request_data}")
            
            response = requests.post(
                f"{self.base_url}/items",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json=request_data
            )
            
            if response.status_code == 201:
                data = response.json()
                current_app.logger.info(f"Successfully created item in Zoho: {data}")
                return data.get('item')
            elif response.status_code == 401:
                current_app.logger.info("Token expired, attempting to refresh")
                if self.refresh_token():
                    return self.create_item_in_zoho(item_data)
            
            current_app.logger.error(f"Failed to create item in Zoho: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error creating item in Zoho: {str(e)}")
            return None

    def update_item_in_zoho(self, zoho_item_id: str, item_data: Dict[str, Any]) -> bool:
        """Update an existing item in Zoho Inventory."""
        access_token = self.get_access_token()
        if not access_token:
            current_app.logger.error("No access token available")
            return False
        
        try:
            current_app.logger.info(f"Updating item {zoho_item_id} in Zoho")
            
            # Determine status based on expiry date
            expiry_date = datetime.strptime(item_data['expiry_date'], '%Y-%m-%d').date()
            current_date = datetime.now().date()
            status = "inactive" if expiry_date <= current_date else "active"
            
            # Prepare the update data
            update_data = {
                "name": item_data['name'],
                "unit": item_data['unit'],
                "stock_on_hand": item_data['quantity'],
                "description": item_data.get('description', ''),
                "status": status
            }
            
            # Only include rate if selling_price is provided
            if 'selling_price' in item_data and item_data['selling_price'] is not None:
                update_data["rate"] = float(item_data['selling_price'])
            
            response = requests.put(
                f"{self.base_url}/items/{zoho_item_id}",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json=update_data
            )
            
            if response.status_code == 200:
                current_app.logger.info(f"Successfully updated item {zoho_item_id} in Zoho with status: {status}")
                return True
            elif response.status_code == 401:
                current_app.logger.info("Token expired, attempting to refresh")
                if self.refresh_token():
                    return self.update_item_in_zoho(zoho_item_id, item_data)
            
            current_app.logger.error(f"Failed to update item in Zoho: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error updating item in Zoho: {str(e)}")
            return False

    def delete_item_in_zoho(self, zoho_item_id: str) -> bool:
        """Mark an item as inactive in Zoho Inventory."""
        access_token = self.get_access_token()
        if not access_token:
            current_app.logger.error("No access token available")
            return False
        
        try:
            current_app.logger.info(f"Marking item {zoho_item_id} as inactive in Zoho")
            response = requests.put(
                f"{self.base_url}/items/{zoho_item_id}",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json={
                    "status": "inactive"
                }
            )
            
            if response.status_code == 200:
                current_app.logger.info(f"Successfully marked item {zoho_item_id} as inactive in Zoho")
                return True
            elif response.status_code == 401:
                current_app.logger.info("Token expired, attempting to refresh")
                if self.refresh_token():
                    return self.delete_item_in_zoho(zoho_item_id)
            
            current_app.logger.error(f"Failed to mark item as inactive in Zoho: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error marking item as inactive in Zoho: {str(e)}")
            return False

    def check_and_update_expired_items(self, user: User) -> bool:
        """Check for expired items and update their status in Zoho."""
        try:
            # Get all items for the user
            items = Item.query.filter_by(user_id=user.id).all()
            current_date = datetime.now().date()
            
            for item in items:
                if not item.zoho_item_id or not item.expiry_date:
                    continue
                    
                # Check if item has expired
                if item.expiry_date.date() <= current_date:
                    # Update item status in Zoho to inactive
                    self.update_item_in_zoho(item.zoho_item_id, {
                        "name": item.name,
                        "unit": item.unit,
                        "rate": item.selling_price,
                        "stock_on_hand": item.quantity,
                        "description": item.description or "",
                        "expiry_date": item.expiry_date.strftime('%Y-%m-%d'),
                        "status": "inactive"
                    })
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error checking expired items: {str(e)}")
            return False

    def get_item_status(self, zoho_item_id: str) -> Optional[str]:
        """Get the status of an item in Zoho Inventory."""
        access_token = self.get_access_token()
        if not access_token:
            current_app.logger.error("No access token available")
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/items/{zoho_item_id}",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('item', {}).get('status')
            elif response.status_code == 401:
                current_app.logger.info("Token expired, attempting to refresh")
                if self.refresh_token():
                    return self.get_item_status(zoho_item_id)
            
            current_app.logger.error(f"Failed to get item status from Zoho: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error getting item status from Zoho: {str(e)}")
            return None

    def logout(self):
        """Logout from Zoho and clear access token."""
        try:
            # Clear the tokens from the user record
            self.user.zoho_access_token = None
            self.user.zoho_refresh_token = None
            self.user.zoho_token_expires_at = None
            self.user.zoho_organization_id = None
            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Error logging out from Zoho: {str(e)}")
            return False

    def update_item_status_in_zoho(self, zoho_item_id: str, status: str) -> bool:
        """Update item status in Zoho."""
        access_token = self.get_access_token()
        if not access_token:
            current_app.logger.error("No access token available")
            return False
            
        try:
            current_app.logger.info(f"Updating item {zoho_item_id} status to {status} in Zoho")
            
            response = requests.put(
                f"{self.base_url}/items/{zoho_item_id}",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json={
                    'status': status
                }
            )
            
            if response.status_code == 200:
                current_app.logger.info(f"Successfully updated item {zoho_item_id} status to {status}")
                return True
            elif response.status_code == 401:
                current_app.logger.info("Token expired, attempting to refresh")
                if self.refresh_token():
                    return self.update_item_status_in_zoho(zoho_item_id, status)
            
            current_app.logger.error(f"Failed to update item status in Zoho: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error updating item status in Zoho: {str(e)}")
            return False

    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Optional[Dict]:
        """Make a request to the Zoho API."""
        access_token = self.get_access_token()
        if not access_token:
            current_app.logger.error("No access token available")
            return None
            
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}{endpoint}"
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if data else None,
                params=params if params else None
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # Token expired, try to refresh
                if self.refresh_token():
                    return self._make_request(method, endpoint, data, params)
                    
            current_app.logger.error(f"API request failed: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error making API request: {str(e)}")
            return None 