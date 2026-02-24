#!/usr/bin/env python3
"""
Create test user for testing
"""

import sqlite3
import hashlib
from datetime import datetime

def create_test_user():
    """Create test user in database"""
    print("🧪 Creating test user...")
    
    # Connect to database
    conn = sqlite3.connect('backend/flight_booking.db')
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id, email FROM USERS WHERE email = ?", ("test@safetravelapp.com",))
    existing_user = cursor.fetchone()
    
    if existing_user:
        print(f"✅ Test user already exists: ID {existing_user[0]}, Email: {existing_user[1]}")
        conn.close()
        return
    
    # Create password hash (simple hash for development)
    password = "testpassword123"
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Insert test user
    now = datetime.utcnow()
    cursor.execute("""
        INSERT INTO USERS (email, username, full_name, password_hash, phone, is_active, created_at, last_login)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "test@safetravelapp.com",
        "testuser",
        "Test User",
        password_hash,
        "+1234567890",
        True,
        now,
        now
    ))
    
    conn.commit()
    user_id = cursor.lastrowid
    
    print(f"✅ Test user created successfully!")
    print(f"   ID: {user_id}")
    print(f"   Email: test@safetravelapp.com")
    print(f"   Password: testpassword123")
    print(f"   Full Name: Test User")
    
    conn.close()

if __name__ == "__main__":
    create_test_user()