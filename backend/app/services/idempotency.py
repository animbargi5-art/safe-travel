from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.idempotency import IdempotencyKey


def check_and_store_key(db: Session, key: str) -> bool:
    try:
        db.add(IdempotencyKey(key=key))
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False
