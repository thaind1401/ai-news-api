from datetime import datetime, timedelta, timezone
from typing import List, Optional, Sequence, Tuple

from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session, joinedload

from app.database.db import SessionLocal
from app.database.models import Company, Signal, Source, Topic


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def list_signals(
    db: Session,
    page: int = 1,
    size: int = 10,
    query_text: Optional[str] = None,
    source: Optional[str] = None,
    company: Optional[str] = None,
    topic: Optional[str] = None,
    event_type: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    sort: str = "newest",
) -> Tuple[Sequence[Signal], int]:
    query = db.query(Signal).filter(
        Signal.signal_status == "active",
        Signal.visibility == "public",
    )

    if source:
        query = query.join(Source).filter(Source.name.ilike(source.strip()))

    if company:
        query = query.join(Company).filter(Company.name.ilike(company.strip()))

    if topic:
        query = query.join(Topic).filter(Topic.name.ilike(topic.strip()))

    if query_text:
        keyword = f"%{query_text.strip()}%"
        query = query.filter(
            or_(
                Signal.title.ilike(keyword),
                Signal.raw_excerpt.ilike(keyword),
                Signal.source_url.ilike(keyword),
            )
        )

    if event_type:
        query = query.filter(Signal.event_type == event_type.strip())

    if from_date:
        query = query.filter(Signal.published_at >= from_date)

    if to_date:
        query = query.filter(Signal.published_at <= to_date)

    total = query.count()

    if sort == "oldest":
        query = query.order_by(asc(Signal.published_at), asc(Signal.id))
    else:
        query = query.order_by(desc(Signal.published_at), desc(Signal.id))

    items = (
        query.options(
            joinedload(Signal.source),
            joinedload(Signal.company),
            joinedload(Signal.primary_topic),
            joinedload(Signal.ai_enrichment),
        )
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return items, total


def get_signal_by_id(db: Session, signal_id: int) -> Optional[Signal]:
    return (
        db.query(Signal)
        .options(
            joinedload(Signal.source),
            joinedload(Signal.company),
            joinedload(Signal.primary_topic),
            joinedload(Signal.ai_enrichment),
        )
        .filter(
            Signal.id == signal_id,
            Signal.signal_status == "active",
            Signal.visibility == "public",
        )
        .first()
    )


def list_topics(db: Session) -> List[str]:
    rows = db.query(Topic.name).order_by(asc(Topic.name)).all()
    return [row[0] for row in rows]


def list_companies(db: Session) -> List[str]:
    rows = db.query(Company.name).order_by(asc(Company.name)).all()
    return [row[0] for row in rows]


def list_trending_signals(db: Session, limit: int = 10, within_hours: int = 24) -> Sequence[Signal]:
    since = datetime.now(timezone.utc) - timedelta(hours=within_hours)
    items = (
        db.query(Signal)
        .options(
            joinedload(Signal.source),
            joinedload(Signal.company),
            joinedload(Signal.primary_topic),
            joinedload(Signal.ai_enrichment),
        )
        .filter(
            Signal.signal_status == "active",
            Signal.visibility == "public",
            Signal.published_at.isnot(None),
            Signal.published_at >= since,
        )
        .order_by(desc(Signal.published_at), desc(Signal.id))
        .limit(limit)
        .all()
    )

    if items:
        return items

    return (
        db.query(Signal)
        .options(
            joinedload(Signal.source),
            joinedload(Signal.company),
            joinedload(Signal.primary_topic),
            joinedload(Signal.ai_enrichment),
        )
        .filter(
            Signal.signal_status == "active",
            Signal.visibility == "public",
        )
        .order_by(desc(Signal.published_at), desc(Signal.id))
        .limit(limit)
        .all()
    )
