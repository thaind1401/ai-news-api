from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.services.news_service import get_db, get_news as get_news_service

router = APIRouter()

@router.get("/news")
def get_news(db: Session = Depends(get_db)):
    rows = get_news_service(db, skip=0, limit=10)
    data = [
        {
            "id": n.id,
            "title": n.title,
            "sub_title": n.sub_title,
            "image": n.image,
            "author": n.author,
            "category": n.category,
            "content": n.content,
            "published_at": n.published_at.isoformat() if n.published_at else None,
        }
        for n in rows
    ]
    return {"data": data}