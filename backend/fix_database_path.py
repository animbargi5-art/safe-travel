#!/usr/bin/env python3
"""
Fix database path issue by copying data to the correct location
"""

import sqlite3
import os
import shutil

def fix_database_path():
    """Copy database to correct location for SQLAlchemy"""
    print("🧪 Fixing database path...")
    
    # Source database (where our data is)
    source_db = "backend/flight_booking.db"
    
    # Target database (where SQLAlchemy expects it)
    target_db = "flight_booking.db"
    
    if os.path.exists(source_db):
        print(f"✅ Source database found: {source_db}")
        
        # Copy database to correct location
        shutil.copy2(source_db, target_db)
        print(f"✅ Database copied to: {target_db}")
        
        # Verify the copy
        conn = sqlite3.connect(target_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM USERS")
        user_count = cursor.fetchone()[0]
        print(f"✅ Users in copied database: {user_count}")
        conn.close()
        
    else:
        print(f"❌ Source database not found: {source_db}")

if __name__ == "__main__":
    fix_database_path()