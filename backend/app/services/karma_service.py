from sqlalchemy.orm import Session
from app.models.karma import KarmaLog


def record_karma(db: Session, entity, entity_id, action, details=None):
    log = KarmaLog(
        entity_type=entity,
        entity_id=entity_id,
        action=action,
        details=details,
    )
    db.add(log)
