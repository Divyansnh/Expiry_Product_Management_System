from app import create_app
from sqlalchemy import inspect
from app.core.extensions import db

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    columns = inspector.get_columns('users')
    print("\nColumns in users table:")
    for column in columns:
        print(f"- {column['name']}: {column['type']}") 