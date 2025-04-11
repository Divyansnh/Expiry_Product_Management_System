import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.core.extensions import db
from sqlalchemy import inspect

def check_database_schema():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        print("\n=== Database Tables ===")
        for table_name in inspector.get_table_names():
            print(f"\nTable: {table_name}")
            columns = inspector.get_columns(table_name)
            for column in columns:
                print(f"  Column: {column['name']} ({column['type']})")
            
            # Check indexes
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print("\n  Indexes:")
                for index in indexes:
                    print(f"    {index['name']}: {index['column_names']}")
            
            # Check foreign keys
            foreign_keys = inspector.get_foreign_keys(table_name)
            if foreign_keys:
                print("\n  Foreign Keys:")
                for fk in foreign_keys:
                    print(f"    {fk['name']}: {fk['referred_table']}.{fk['referred_columns']}")

if __name__ == '__main__':
    check_database_schema() 