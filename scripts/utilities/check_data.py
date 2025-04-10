from sqlalchemy import create_engine, text

def check_database_data():
    engine = create_engine('postgresql://localhost/expiry_tracker_v2')
    
    with engine.connect() as conn:
        # Check users count and basic info
        result = conn.execute(text("""
            SELECT COUNT(*), 
                   COUNT(DISTINCT id) as unique_users,
                   COUNT(CASE WHEN is_admin = true THEN 1 END) as admin_count
            FROM users
        """))
        users_stats = result.fetchone()
        print("\nUsers Statistics:")
        print(f"Total users: {users_stats[0]}")
        print(f"Unique users: {users_stats[1]}")
        print(f"Admin users: {users_stats[2]}")
        
        # Sample some user data
        result = conn.execute(text("""
            SELECT id, username, email, is_admin, is_active, is_verified
            FROM users
            LIMIT 5
        """))
        print("\nSample Users:")
        for row in result:
            print(f"User {row.id}: {row.username} ({row.email})")
            print(f"  - Admin: {row.is_admin}")
            print(f"  - Active: {row.is_active}")
            print(f"  - Verified: {row.is_verified}")
        
        # Check items count
        result = conn.execute(text("SELECT COUNT(*) FROM items"))
        items_count = result.scalar()
        print(f"\nTotal items: {items_count}")
        
        # Check notifications count
        result = conn.execute(text("SELECT COUNT(*) FROM notifications"))
        notifications_count = result.scalar()
        print(f"Total notifications: {notifications_count}")
        
        # Check reports count
        result = conn.execute(text("SELECT COUNT(*) FROM reports"))
        reports_count = result.scalar()
        print(f"Total reports: {reports_count}")

if __name__ == '__main__':
    check_database_data() 