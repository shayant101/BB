"""
Fix datetime format issues in vendor profiles
"""

import sqlite3
from datetime import datetime

def fix_datetime_formats():
    """Fix datetime format issues in vendor profiles"""
    
    # Connect to database
    conn = sqlite3.connect('bistroboard.db')
    cursor = conn.cursor()
    
    print("🔧 Fixing datetime format issues...")
    
    try:
        # Get all vendor profiles with string datetime values
        cursor.execute("""
            SELECT id, created_at, updated_at 
            FROM vendor_profiles 
            WHERE typeof(updated_at) = 'text'
        """)
        
        profiles_to_fix = cursor.fetchall()
        
        if not profiles_to_fix:
            print("✅ No datetime format issues found!")
            return
        
        print(f"📝 Found {len(profiles_to_fix)} profiles with datetime format issues")
        
        for profile_id, created_at, updated_at in profiles_to_fix:
            # Convert string datetime to proper datetime
            try:
                if isinstance(updated_at, str):
                    # Parse the ISO format string and convert back to datetime
                    if 'T' in updated_at:
                        dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    else:
                        dt = datetime.fromisoformat(updated_at)
                    
                    # Update the record with proper datetime
                    cursor.execute("""
                        UPDATE vendor_profiles 
                        SET updated_at = ? 
                        WHERE id = ?
                    """, (dt, profile_id))
                    
                    print(f"   ✅ Fixed profile ID {profile_id}")
            except Exception as e:
                print(f"   ❌ Error fixing profile ID {profile_id}: {e}")
        
        conn.commit()
        print(f"🎉 Successfully fixed {len(profiles_to_fix)} vendor profiles!")
        
    except Exception as e:
        print(f"❌ Error fixing datetime formats: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_datetime_formats()