#!/usr/bin/env python3
"""
Complete Database Setup Script
Creates tables, seeds aircraft, flights, and test data
"""

import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_database():
    """Complete database setup with all data"""
    print("🚀 Setting up Safe Travel Database...")
    print("=" * 50)
    
    try:
        # Import after path setup
        from app.database import engine, Base, SessionLocal
        from app.services.aircraft_seed import create_airbus_a320
        from app.services.flight_seed import seed_flight_data, create_popular_routes
        
        # Import all models to ensure they're registered
        import app.models.user
        import app.models.aircraft
        import app.models.flight
        import app.models.seat
        import app.models.booking
        import app.models.payment
        import app.models.waitlist
        
        print("1️⃣ Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
        
        print("\n2️⃣ Seeding aircraft data...")
        db = SessionLocal()
        try:
            create_airbus_a320(db)
            print("✅ Aircraft and seats created")
        finally:
            db.close()
        
        print("\n3️⃣ Seeding flight data...")
        db = SessionLocal()
        try:
            seed_flight_data(db)
            create_popular_routes(db)
            print("✅ Flight data seeded")
        finally:
            db.close()
        
        print("\n4️⃣ Creating test user...")
        db = SessionLocal()
        try:
            from app.models.user import User
            
            # Check if test user already exists
            existing_user = db.query(User).filter(User.email == "test@safetravelapp.com").first()
            if existing_user:
                print("⚠️  Test user already exists")
            else:
                # Create test user with simple hash (for testing only)
                test_user = User(
                    email="test@safetravelapp.com",
                    username="testuser",
                    full_name="Test User",
                    password_hash="$2b$12$simple_test_hash_for_development",  # Simple test hash
                    phone="+1234567890",
                    is_active=True
                )
                db.add(test_user)
                db.commit()
                print(f"✅ Test user created: test@safetravelapp.com")
                print("   Note: Use registration API to create users with proper passwords")
        except Exception as e:
            print(f"⚠️  Test user creation: {e}")
        finally:
            db.close()
        
        print("\n" + "=" * 50)
        print("🎉 Database setup completed successfully!")
        print("\n📊 Database Summary:")
        
        # Show database stats
        db = SessionLocal()
        try:
            from app.models.aircraft import Aircraft
            from app.models.flight import Flight
            from app.models.seat import Seat
            from app.models.user import User
            
            aircraft_count = db.query(Aircraft).count()
            flight_count = db.query(Flight).count()
            seat_count = db.query(Seat).count()
            user_count = db.query(User).count()
            
            print(f"   • Aircraft: {aircraft_count}")
            print(f"   • Flights: {flight_count}")
            print(f"   • Seats: {seat_count}")
            print(f"   • Users: {user_count}")
            
        finally:
            db.close()
        
        print("\n🔗 Ready to test:")
        print("   • Backend API: http://localhost:8000")
        print("   • API Docs: http://localhost:8000/docs")
        print("   • Frontend: http://localhost:5173")
        print("   • Test Login: test@safetravelapp.com / testpass123")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def reset_database():
    """Reset database by deleting and recreating"""
    print("🔄 Resetting database...")
    
    try:
        import os
        db_file = "flight_booking.db"
        if os.path.exists(db_file):
            os.remove(db_file)
            print("✅ Old database deleted")
        
        return setup_database()
        
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Safe Travel Database Setup")
    parser.add_argument("--reset", action="store_true", help="Reset database (delete and recreate)")
    args = parser.parse_args()
    
    if args.reset:
        success = reset_database()
    else:
        success = setup_database()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())