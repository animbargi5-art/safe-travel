from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, SessionLocal
from app.routes import flights, seats, booking, admin, health, auth, payment, email, group_booking, ml, websocket, reporting, waitlist, ultra_fast_booking, nanosecond_booking, live_monitoring, currency, smart_recommendations, voice_booking, social_booking, loyalty_program
from app.services.expire_bookings import expire_old_bookings
from app.services.scheduler import start_scheduler
from app.services.aircraft_seed import create_airbus_a320
from app.services.flight_seed import seed_flight_data, create_popular_routes
from app.services.db_optimizer import get_db_optimizer

app = FastAPI(title="Flight Booking API - Ultra-Fast Edition ⚡")

# Initialize database optimizer for ultra-fast operations
db_optimizer = get_db_optimizer("sqlite:///./flight_booking.db")

# Routers
app.include_router(auth.router)
app.include_router(flights.router)
app.include_router(seats.router)
app.include_router(booking.router)
app.include_router(ultra_fast_booking.router)  # ⚡ Ultra-fast booking routes
app.include_router(nanosecond_booking.router)  # 🚀 TRUE NANOSECOND booking routes
app.include_router(live_monitoring.router)  # 🔍 Live monitoring dashboard
app.include_router(currency.router)  # 💱 Multi-currency support
app.include_router(smart_recommendations.router)  # 🤖 AI-powered recommendations
app.include_router(voice_booking.router)  # 🎤 Voice-powered booking
app.include_router(social_booking.router)  # 👥 Social booking with friends
app.include_router(loyalty_program.router)  # 🏆 Loyalty program & rewards
app.include_router(group_booking.router)
app.include_router(payment.router)
app.include_router(email.router)
app.include_router(admin.router)
app.include_router(ml.router)
app.include_router(websocket.router)
app.include_router(reporting.router)
app.include_router(waitlist.router)
app.include_router(health.router)

# CORS - Updated for mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173",
        "http://192.168.31.230:5173",  # Mobile access
        "http://192.168.31.230:3000",  # Alternative port
        "*"  # Allow all origins for development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables once
Base.metadata.create_all(bind=engine)

# Expiry middleware
@app.middleware("http")
async def expire_seats_middleware(request, call_next):
    db = SessionLocal()
    try:
        expire_old_bookings(db)
    finally:
        db.close()
    return await call_next(request)

# Scheduler startup
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        create_airbus_a320(db)
        seed_flight_data(db)
        create_popular_routes(db)
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Flight Booking API Running"}
