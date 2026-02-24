#!/usr/bin/env python3
"""
Update test user password to work with our auth system
"""

import sqlite3
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.auth_service import get_password_hash

def update_test_password():
    """Update test user password"""
    print("🧪 Updating test user password...")
    
    # Connect to database
    conn = sqlite3.connect('flight_booking.db')
    cursor = conn.cursor()
    
    # Generate proper password hash
    password = "testpass123"
    password_hash = get_password_hash(password)
    
    print(f"Password: {password}")
    print(f"New hash: {password_hash[:50]}...")
    
    # Update user password
    cursor.execute("UPDATE USERS SET password_hash = ? WHERE email = ?", 
                   (password_hash, "test@safetravelapp.com"))
    
    conn.commit()
    
    # Verify update
    cursor.execute("SELECT email, password_hash FROM USERS WHERE email = ?", 
                   ("test@safetravelapp.com",))
    user = cursor.fetchone()
    
    if user:
        print(f"✅ Password updated for: {user[0]}")
        print(f"   New hash: {user[1][:50]}...")
    
    conn.close()

if __name__ == "__main__":
    update_test_password()