"""
Database migration script to add Admin Command Center fields
"""

import sqlite3
from pathlib import Path

def migrate_database():
    """Add new admin fields to existing database"""
    db_path = Path("bistroboard.db")
    
    if not db_path.exists():
        print("Database file not found. Creating new database with admin features.")
        return
    
    print("Migrating existing database for Admin Command Center...")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if admin columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations = []
        
        # Add new columns if they don't exist
        if 'is_active' not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
        
        if 'status' not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN status VARCHAR DEFAULT 'active'")
        
        if 'deactivation_reason' not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN deactivation_reason TEXT")
        
        if 'deactivated_by' not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN deactivated_by INTEGER")
        
        if 'deactivated_at' not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN deactivated_at DATETIME")
        
        if 'last_login_at' not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN last_login_at DATETIME")
        
        # Execute migrations
        for migration in migrations:
            print(f"Executing: {migration}")
            cursor.execute(migration)
        
        # Create new tables
        print("Creating admin audit log table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                target_user_id INTEGER,
                action VARCHAR NOT NULL,
                details JSON,
                ip_address VARCHAR,
                user_agent VARCHAR,
                session_id VARCHAR,
                created_at DATETIME NOT NULL,
                FOREIGN KEY(admin_id) REFERENCES users (id),
                FOREIGN KEY(target_user_id) REFERENCES users (id)
            )
        """)
        
        print("Creating user event log table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_event_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_type VARCHAR NOT NULL,
                details JSON,
                ip_address VARCHAR,
                user_agent VARCHAR,
                created_at DATETIME NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users (id)
            )
        """)
        
        print("Creating impersonation sessions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS impersonation_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                target_user_id INTEGER NOT NULL,
                session_token VARCHAR UNIQUE NOT NULL,
                expires_at DATETIME NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                ended_at DATETIME,
                created_at DATETIME NOT NULL,
                FOREIGN KEY(admin_id) REFERENCES users (id),
                FOREIGN KEY(target_user_id) REFERENCES users (id)
            )
        """)
        
        # Update existing users to have default admin field values
        print("Updating existing users with default admin field values...")
        cursor.execute("""
            UPDATE users 
            SET is_active = 1, status = 'active' 
            WHERE is_active IS NULL OR status IS NULL
        """)
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()