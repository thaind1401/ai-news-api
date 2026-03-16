import httpx
import asyncio
import logging
import json

from bs4 import BeautifulSoup

from app.services.ingestion_service import get_or_create_source, upsert_signal_from_news_detail
from app.database.db import SessionLocal
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
    stats = {
        "raw_items_created": 0,
        "signals_created": 0,
        "enrichments_created": 0,
        "duplicates_skipped": 0,
    }

    db = SessionLocal()
    try:
        source = get_or_create_source(
            db=db,
            name="vnexpress",
            base_url="https://vnexpress.net",
            source_type="news_site",
        )

        for i, result in enumerate(results):
            if isinstance(result, Exception) or result is None:
                logger.warning("Skip link due to crawl error: %s | error=%s", links[i], result)
                continue

            news_detail = result
            if not news_detail.get("title"):
                continue

            raw_created, signal_created, enrichment_created, skipped_duplicate = upsert_signal_from_news_detail(
                db=db,
                source=source,
                source_url=links[i],
                news_detail=news_detail,
            )
            stats["raw_items_created"] += 1 if raw_created else 0
            stats["signals_created"] += 1 if signal_created else 0
            stats["enrichments_created"] += 1 if enrichment_created else 0
            stats["duplicates_skipped"] += 1 if skipped_duplicate else 0

            saved_items.append(
                {
                    "title": news_detail.get("title", ""),
                    "published_at": str(news_detail.get("published_at", "")),
                    "category": news_detail.get("category", ""),
                    "source_url": links[i],
                }
            )

        db.commit()
        logger.info("Crawler saved %s items", len(saved_items))
        logger.info("Crawler stats: %s", json.dumps(stats, ensure_ascii=False))
        logger.info("Crawler data: %s", json.dumps(saved_items, ensure_ascii=False))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
