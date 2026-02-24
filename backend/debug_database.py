#!/usr/bin/env python3
"""
Debug database connection and tables
"""

import sqlite3
import sys
import os
from sqlalchemy import text

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.database import SessionLocal, engine

def debug_database():
    """Debug database connection"""
    print("🧪 Debugging database connection...")
    
    # Test SQLite direct connection
    print("\n1. Testing SQLite direct connection...")
    try:
        conn = sqlite3.connect('backend/flight_booking.db')
        cursor = conn.cursor()
        
        # List tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"   Tables found: {[table[0] for table in tables]}")
        
        # Check USERS table
        cursor.execute("SELECT COUNT(*) FROM USERS")
        user_count = cursor.fetchone()[0]
        print(f"   Users in USERS table: {user_count}")
        
        # Get sample user
        cursor.execute("SELECT id, email, full_name FROM USERS LIMIT 1")
        sample_user = cursor.fetchone()
        if sample_user:
            print(f"   Sample user: ID={sample_user[0]}, Email={sample_user[1]}, Name={sample_user[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ SQLite error: {e}")
    
    # Test SQLAlchemy connection
    print("\n2. Testing SQLAlchemy connection...")
    try:
        db = SessionLocal()
        
        # Test raw SQL query
        result = db.execute(text("SELECT COUNT(*) FROM USERS")).fetchone()
        print(f"   Users via SQLAlchemy raw SQL: {result[0]}")
        
        # Test ORM query
        from app.models.user import User
        user_count = db.query(User).count()
        print(f"   Users via SQLAlchemy ORM: {user_count}")
        
        # Get sample user via ORM
        sample_user = db.query(User).first()
        if sample_user:
            print(f"   Sample user via ORM: ID={sample_user.id}, Email={sample_user.email}")
        else:
            print("   ❌ No users found via ORM")
        
        db.close()
        
    except Exception as e:
        print(f"   ❌ SQLAlchemy error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_database()