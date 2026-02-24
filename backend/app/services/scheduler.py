from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.services.expire_bookings import expire_old_bookings


def start_scheduler():
    scheduler = BackgroundScheduler()

    def expire_job():
        db = SessionLocal()
        try:
            expired = expire_old_bookings(db)
            if expired:
                print(f"[SCHEDULER] Expired {expired} bookings")
        finally:
            db.close()

    # Run every minute
    scheduler.add_job(expire_job, "interval", minutes=1)
    scheduler.start()

    return scheduler
