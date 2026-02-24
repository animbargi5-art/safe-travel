#!/usr/bin/env python3
"""
Check and fix user password
"""

import sqlite3
import hashlib
from datetime import datetime

def check_and_fix_password():
    """Check and fix test user password"""
    print("🧪 Checking test user password...")
    
    # Connect to database
    conn = sqlite3.connect('backend/flight_booking.db')
    cursor = conn.cursor()
    
    # Get user info
    cursor.execute("SELECT id, email, password_hash FROM USERS WHERE email = ?", ("test@safetravelapp.com",))
    user = cursor.fetchone()
    
    if not user:
        print("❌ Test user not found!")
        conn.close()
        return
    
    user_id, email, stored_hash = user
    print(f"User ID: {user_id}")
    print(f"Email: {email}")
    print(f"Stored hash: {stored_hash[:50]}...")
    
    # Test password
    test_password = "testpassword123"
    simple_hash = hashlib.sha256(test_password.encode()).hexdigest()
    
    print(f"Expected hash: {simple_hash[:50]}...")
    
    if stored_hash == simple_hash:
        print("✅ Password hash matches!")
    else:
        print("❌ Password hash doesn't match. Updating...")
        
        # Update password hash
        cursor.execute("UPDATE USERS SET password_hash = ? WHERE id = ?", (simple_hash, user_id))
        conn.commit()
        
        print("✅ Password hash updated!")
    
    conn.close()

if __name__ == "__main__":
    check_and_fix_password()