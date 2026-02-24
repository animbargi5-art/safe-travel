#!/usr/bin/env python3
"""
Check Available Routes
Find what routes actually exist in the database
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_routes():
    """Check available routes in the database"""
    print("🔍 Checking Available Flight Routes...")
    print("=" * 50)
    
    try:
        from app.database import SessionLocal
        from app.models.flight import Flight
        from sqlalchemy import func
        
        db = SessionLocal()
        
        # Check Bangkok routes
        print("\n✈️  FROM BANGKOK:")
        bangkok_routes = db.query(
            Flight.to_city,
            func.count(Flight.id).label('flight_count')
        ).filter(
            Flight.from_city == "Bangkok"
        ).group_by(Flight.to_city).all()
        
        if bangkok_routes:
            for route in bangkok_routes:
                print(f"   Bangkok → {route[0]} ({route[1]} flights)")
        else:
            print("   No flights from Bangkok found")
        
        # Check Indore routes
        print("\n✈️  TO INDORE:")
        indore_routes = db.query(
            Flight.from_city,
            func.count(Flight.id).label('flight_count')
        ).filter(
            Flight.to_city == "Indore"
        ).group_by(Flight.from_city).all()
        
        if indore_routes:
            for route in indore_routes:
                print(f"   {route[0]} → Indore ({route[1]} flights)")
        else:
            print("   No flights to Indore found")
        
        # Check popular routes
        print("\n🔥 TOP 10 POPULAR ROUTES:")
        popular_routes = db.query(
            Flight.from_city,
            Flight.to_city,
            func.count(Flight.id).label('flight_count')
        ).group_by(
            Flight.from_city, Flight.to_city
        ).order_by(
            func.count(Flight.id).desc()
        ).limit(10).all()
        
        for i, route in enumerate(popular_routes, 1):
            print(f"   {i}. {route[0]} → {route[1]} ({route[2]} flights)")
        
        # Suggest alternative searches
        print("\n💡 SUGGESTED SEARCHES:")
        print("   Try these routes that have flights:")
        
        # Get some sample routes
        sample_routes = db.query(
            Flight.from_city,
            Flight.to_city
        ).distinct().limit(10).all()
        
        for route in sample_routes:
            print(f"   • {route[0]} → {route[1]}")
        
        db.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Route check failed: {e}")
        return False

def main():
    """Main function"""
    success = check_routes()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())