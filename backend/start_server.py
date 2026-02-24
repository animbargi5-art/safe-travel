#!/usr/bin/env python3
"""
Safe Travel Backend Server Startup Script
Starts the FastAPI server with all features enabled
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    print("🚀 Starting Safe Travel Backend Server...")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("⚠️  .env file not found. Using default configuration.")
    else:
        print("✅ .env file found")
    
    # Check if database exists
    db_file = backend_dir / "flight_booking.db"
    if not db_file.exists():
        print("⚠️  Database file not found. It will be created automatically.")
    else:
        print("✅ Database file found")
    
    print("\n🌟 Features Available:")
    print("   • Flight Search & Booking")
    print("   • AI Seat Allocation")
    print("   • Payment Processing (Stripe)")
    print("   • Real-time Notifications (WebSocket)")
    print("   • Email Notifications")
    print("   • Group Bookings")
    print("   • Admin Dashboard")
    print("   • Machine Learning Recommendations")
    print("   • Business Intelligence & Analytics")
    print("   • Advanced Security & Fraud Detection")
    
    print("\n📡 API Endpoints will be available at:")
    print("   • Main API: http://localhost:8000")
    print("   • Interactive Docs: http://localhost:8000/docs")
    print("   • WebSocket: ws://localhost:8000/ws/notifications/{token}")
    
    print("\n🔧 CORS enabled for:")
    print("   • http://localhost:3000 (React default)")
    print("   • http://localhost:5173 (Vite default)")
    
    print("\n" + "=" * 50)
    print("Starting server... Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())