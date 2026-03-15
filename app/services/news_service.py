from app.database.db import SessionLocal
from app.database.models import News
from sqlalchemy import desc
from sqlalchemy.orm import Session
from typing import List, Optional

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_news(db: Session, skip: int = 0, limit: int = 10) -> List[News]:
    return db.query(News).order_by(desc(News.published_at), desc(News.id)).offset(skip).limit(limit).all()

def get_news_by_id(db: Session, news_id: int) -> Optional[News]:
    return db.query(News).filter(News.id == news_id).first()

def create_news(
    db: Session,
    title: str,
    content: str,
    published_at=None,
    sub_title: str = None,
    image: str = None,
    author: str = None,
    category: str = None,
    auto_commit: bool = True,
):
    news = News(
        title=title,
        sub_title=sub_title,
        image=image,
        author=author,
        category=category,
        content=content,
        published_at=published_at,
    )
    db.add(news)
    if auto_commit:
        db.commit()
        db.refresh(news)
    return news
