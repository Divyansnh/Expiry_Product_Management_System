import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import User
from app.core.extensions import db

app = create_app()

with app.app_context():
    print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # List all users
    print("\nAll users in database:")
    all_users = User.query.all()
    for user in all_users:
        print(f"Username: {user.username}, Email: {user.email}, Verified: {user.is_verified}")
    
    print("\nSearching for specific user:")
    user = User.query.filter_by(email='divyanshsingh1800@gmail.com').first()
    if user:
        print(f"User found: {user.username}")
        print(f"Is verified: {user.is_verified}")
        print(f"Has password: {bool(user.password_hash)}")
    else:
        print("User not found") 