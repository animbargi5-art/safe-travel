from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database_dep import get_db
from sqlalchemy import text

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
def health_check(db: Session = Depends(get_db)):
    # Use a database-agnostic query
    db.execute(text("SELECT 1"))
    return {"status": "ok"}

