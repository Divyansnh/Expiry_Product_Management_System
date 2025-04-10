from app import app, db
from app.models.user import User
from sqlalchemy import event
from sqlalchemy.pool import Pool

def reset_connections():
    with app.app_context():
        # Reset the connection pool
        engine = db.engine
        engine.dispose()
        
        # Clear any cached metadata
        db.metadata.clear()
        
        # Recreate the tables in the metadata
        db.metadata.reflect(bind=engine)
        
        # Verify the User model
        print("User model columns after reset:")
        for column in User.__table__.columns:
            print(f"- {column.name}: {column.type}")
        
        # Test a query
        try:
            user = User.query.filter_by(email="divyanshsingh1800@gmail.com").first()
            print(f"\nQuery test successful! Found user: {user.username}")
        except Exception as e:
            print(f"\nQuery test failed: {str(e)}")

if __name__ == '__main__':
    reset_connections() 