from sqlalchemy import create_engine, inspect, MetaData, Table
from app.models.user import User
from app import db

def check_connection():
    # Check direct database connection
    engine = create_engine('postgresql://localhost/expiry_tracker_v2')
    inspector = inspect(engine)
    
    print("\n1. Direct Database Check:")
    print("Columns in users table:")
    for column in inspector.get_columns('users'):
        print(f"- {column['name']}: {column['type']}")
    
    # Check SQLAlchemy model mapping
    print("\n2. SQLAlchemy Model Check:")
    metadata = MetaData()
    metadata.reflect(bind=engine)
    users_table = Table('users', metadata, autoload_with=engine)
    print("Columns in SQLAlchemy mapped table:")
    for column in users_table.columns:
        print(f"- {column.name}: {column.type}")
    
    # Check User model definition
    print("\n3. User Model Definition:")
    print("Columns in User model:")
    for column in User.__table__.columns:
        print(f"- {column.name}: {column.type}")

if __name__ == '__main__':
    check_connection() 