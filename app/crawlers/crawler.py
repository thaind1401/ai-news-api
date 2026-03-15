import httpx
import asyncio
import logging
import json
from bs4 import BeautifulSoup
from app.services.news_service import create_news
from app.database.db import SessionLocal
from app.database.models import News
from app.crawlers.news_crawler import crawl_news

logger = logging.getLogger(__name__)

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

async def get_latest_vnexpress_links(n=10):
    url = "https://vnexpress.net/"
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=REQUEST_HEADERS) as client:
        resp = await client.get(url)
        resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")
    links = []
    for a in soup.select('h3.title-news a[href^="https://vnexpress.net/"]'):
        link = a['href']
        if link not in links:
            links.append(link)
        if len(links) >= n:
            break
    return links

async def run_crawler():
    logger.info("Crawler started")
    links = await get_latest_vnexpress_links(10)
    results = await asyncio.gather(*(crawl_news(link) for link in links), return_exceptions=True)
    saved_items = []

    db = SessionLocal()
    try:
        # Chỉ xóa 10 tin cũ nhất, không xóa toàn bảng
        old_news = db.query(News).order_by(News.published_at.asc(), News.id.asc()).limit(10).all()
        for old in old_news:
            db.delete(old)

        for i, result in enumerate(results):
            if isinstance(result, Exception) or result is None:
                logger.warning("Skip link due to crawl error: %s | error=%s", links[i], result)
                continue

            news_detail = result
            if not news_detail.get("title"):
                continue

            create_news(
                db=db,
                title=news_detail.get("title", ""),
                content=news_detail.get("description", ""),
                published_at=news_detail.get("published_at", None),
                sub_title=news_detail.get("sub_title", ""),
                image=news_detail.get("image", ""),
                author=news_detail.get("author", ""),
                category=news_detail.get("category", ""),
                auto_commit=False,
            )
            saved_items.append(
                {
                    "title": news_detail.get("title", ""),
                    "published_at": str(news_detail.get("published_at", "")),
                    "category": news_detail.get("category", ""),
                }
            )

        db.commit()
        logger.info("Crawler saved %s items", len(saved_items))
        logger.info("Crawler data: %s", json.dumps(saved_items, ensure_ascii=False))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
