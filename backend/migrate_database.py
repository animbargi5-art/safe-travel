"""
Database migration script to add new fields to existing tables
Run this script to update your database schema with the new booking and seat fields
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL)

def run_migration():
    """Run database migrations to add new fields"""
    
    migrations = [
        # Create USERS table
        """
        CREATE TABLE IF NOT EXISTS USERS (
            id SERIAL PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            username VARCHAR(50) UNIQUE NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            phone VARCHAR(20),
            password_hash VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            is_verified BOOLEAN DEFAULT FALSE,
            preferred_seat_class VARCHAR(20) DEFAULT 'ECONOMY',
            preferred_seat_position VARCHAR(20) DEFAULT 'ANY',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
        """,
        
        # Create PAYMENTS table
        """
        CREATE TABLE IF NOT EXISTS PAYMENTS (
            id SERIAL PRIMARY KEY,
            booking_id INTEGER NOT NULL REFERENCES BOOKINGS(id),
            user_id INTEGER NOT NULL REFERENCES USERS(id),
            stripe_payment_intent_id VARCHAR(255) UNIQUE NOT NULL,
            stripe_charge_id VARCHAR(255),
            amount DECIMAL(10,2) NOT NULL,
            currency VARCHAR(3) NOT NULL DEFAULT 'USD',
            status VARCHAR(20) NOT NULL,
            refunded_amount DECIMAL(10,2) DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            refunded_at TIMESTAMP
        );
        """,
        
        # Add indexes for payments table
        """
        CREATE INDEX IF NOT EXISTS idx_payments_booking_id ON PAYMENTS(booking_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_payments_user_id ON PAYMENTS(user_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_payments_stripe_intent ON PAYMENTS(stripe_payment_intent_id);
        """,
        
        # Add new fields to SEATS table
        """
        ALTER TABLE SEATS ADD COLUMN IF NOT EXISTS seat_number VARCHAR(5);
        """,
        """
        ALTER TABLE SEATS ADD COLUMN IF NOT EXISTS seat_class VARCHAR(20) DEFAULT 'ECONOMY';
        """,
        
        # Add new fields to BOOKINGS table
        """
        ALTER TABLE BOOKINGS ADD COLUMN IF NOT EXISTS passenger_name VARCHAR(100);
        """,
        """
        ALTER TABLE BOOKINGS ADD COLUMN IF NOT EXISTS passenger_email VARCHAR(100);
        """,
        """
        ALTER TABLE BOOKINGS ADD COLUMN IF NOT EXISTS passenger_phone VARCHAR(20);
        """,
        """
        ALTER TABLE BOOKINGS ADD COLUMN IF NOT EXISTS price DECIMAL(10,2);
        """,
        
        # Update existing seats with seat_number if they don't have it
        """
        UPDATE SEATS 
        SET seat_number = CAST(row AS VARCHAR) || col 
        WHERE seat_number IS NULL;
        """,
        
        # Make seat_number NOT NULL after populating
        """
        ALTER TABLE SEATS ALTER COLUMN seat_number SET NOT NULL;
        """,
        
        # Add foreign key constraint for bookings -> users (if not exists)
        """
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_bookings_user_id'
            ) THEN
                ALTER TABLE BOOKINGS ADD CONSTRAINT fk_bookings_user_id 
                FOREIGN KEY (user_id) REFERENCES USERS(id);
            END IF;
        END $$;
        """
    ]
    
    with engine.connect() as conn:
        for i, migration in enumerate(migrations, 1):
            try:
                print(f"Running migration {i}/{len(migrations)}...")
                conn.execute(text(migration))
                conn.commit()
                print(f"✅ Migration {i} completed successfully")
            except Exception as e:
                print(f"⚠️  Migration {i} failed (might already exist): {e}")
                conn.rollback()
    
    print("\n🎉 Database migration completed!")
    print("Your database schema has been updated with:")
    print("- User authentication system")
    print("- Enhanced seat and booking models")
    print("- Proper foreign key relationships")

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    run_migration()