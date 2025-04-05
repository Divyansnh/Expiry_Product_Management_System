import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.core.extensions import db

app = create_app()

with app.app_context():
    print(f"Database URL from config: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Environment DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    
    # Try to connect to the database
    try:
        db.engine.connect()
        print("Successfully connected to database")
    except Exception as e:
        print(f"Error connecting to database: {e}") 