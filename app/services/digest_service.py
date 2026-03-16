from sqlalchemy.orm import Session


def get_today_digest(db: Session, user_id: int | None = None):
    raise NotImplementedError("digest_service will be implemented in next phase")
