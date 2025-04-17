import psycopg2
from psycopg2.extras import RealDictCursor

try:
    # Connect to the database
    conn = psycopg2.connect(
        dbname="expiry_tracker",
        host="localhost"
    )
    
    # Create a cursor
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if users table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'users'
        );
    """)
    table_exists = cur.fetchone()['exists']
    print(f"Users table exists: {table_exists}")
    
    if table_exists:
        # Get all users
        cur.execute("SELECT id, username, email, is_active FROM users;")
        users = cur.fetchall()
        print("\nUsers in database:")
        for user in users:
            print(f"ID: {user['id']}, Username: {user['username']}, Email: {user['email']}, Active: {user['is_active']}")
    
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close() 