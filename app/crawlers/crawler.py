import httpx
import asyncio
import logging
import json
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.config.source_registry import load_source_registry
from app.services.ingestion_service import (
    get_or_create_source,
    process_pending_signal_enrichments,
    upsert_signal_from_news_detail,
)
from app.database.db import SessionLocal
from app.crawlers.news_crawler import crawl_news

logger = logging.getLogger(__name__)

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


def _text_or_none(value: str | None) -> str:
    return str(value or "").strip()


def _iter_entries(root: ET.Element):
    tag = root.tag.lower()
    if tag.endswith("rss"):
        channel = root.find("channel")
        if channel is not None:
            return channel.findall("item")
    if tag.endswith("feed"):
        return [element for element in root if element.tag.lower().endswith("entry")]
    return []


def _extract_link_from_entry(entry: ET.Element) -> str:
    entry_tag = entry.tag.lower()
    if entry_tag.endswith("item"):
        link = entry.findtext("link")
        return _text_or_none(link)

    if entry_tag.endswith("entry"):
        for element in entry:
            if not element.tag.lower().endswith("link"):
                continue

            href = _text_or_none(element.attrib.get("href"))
            rel = _text_or_none(element.attrib.get("rel"))
            if href and rel in ("", "alternate"):
                return href

            text = _text_or_none(element.text)
            if text:
                return text
    return ""

async def _discover_from_homepage_css(
    client: httpx.AsyncClient,
    discovery: dict[str, Any],
    limit: int,
) -> list[str]:
    url = str(discovery.get("url", "")).strip()
    selector = str(discovery.get("selector", "")).strip()
    if not url or not selector:
        return []

    resp = await client.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")
    links = []
    for a in soup.select(selector):
        link = str(a.get("href", "")).strip()
        if not link:
            continue
        link = urljoin(url, link)
        if not link.startswith("http"):
            continue
        if link not in links:
            links.append(link)
        if len(links) >= limit:
            break
    return links


async def _discover_from_rss(
    client: httpx.AsyncClient,
    discovery: dict[str, Any],
    limit: int,
) -> list[str]:
    url = str(discovery.get("url", "")).strip()
    if not url:
        return []

    resp = await client.get(url)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)

    links: list[str] = []
    for entry in _iter_entries(root):
        link = _extract_link_from_entry(entry)
        if link and link not in links:
            links.append(link)
        if len(links) >= limit:
            break

    return links


async def discover_source_links(
    client: httpx.AsyncClient,
    source_config: dict[str, Any],
) -> list[str]:
    discovery = source_config.get("discovery") or {}
    if not isinstance(discovery, dict):
        return []

    limit = int(source_config.get("max_links", 10) or 10)
    method = str(discovery.get("type", "")).strip().lower()

    if method == "homepage_css":
        return await _discover_from_homepage_css(client=client, discovery=discovery, limit=limit)
    if method == "rss":
        return await _discover_from_rss(client=client, discovery=discovery, limit=limit)
    return []


async def run_crawler():
    logger.info("Crawler started")
    source_configs = load_source_registry()
    if not source_configs:
        logger.warning("No enabled sources found in config")
        return

    stats = {
        "enabled_sources": len(source_configs),
        "processed_sources": 0,
        "fetched_links": 0,
        "raw_items_created": 0,
        "signals_created": 0,
        "signals_published": 0,
        "enrichment_failures": 0,
        "duplicates_skipped": 0,
    }

    db = SessionLocal()
    saved_items = []
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=REQUEST_HEADERS) as client:
            for source_config in source_configs:
                source_name = str(source_config.get("name", "")).strip()
                if not source_name:
                    continue

                try:
                    links = await discover_source_links(client=client, source_config=source_config)
                except Exception as exc:
                    logger.warning("Discover links failed for source=%s error=%s", source_name, exc)
                    continue

                if not links:
                    logger.info("No links discovered for source=%s", source_name)
                    continue

                detail_parser = str(source_config.get("detail_parser", "generic_meta") or "generic_meta")
                results = await asyncio.gather(
                    *(crawl_news(link, parser_type=detail_parser) for link in links),
                    return_exceptions=True,
                )

                source = get_or_create_source(
                    db=db,
                    name=source_name,
                    base_url=str(source_config.get("base_url", "")).strip(),
                    source_type=str(source_config.get("source_type", "news_site") or "news_site"),
                    ingest_method=str(source_config.get("ingest_method", "html") or "html"),
                    risk_level=str(source_config.get("risk_level", "B") or "B"),
                    terms_reviewed=bool(source_config.get("terms_reviewed", False)),
                    robots_reviewed=bool(source_config.get("robots_reviewed", False)),
                    auth_required=bool(source_config.get("auth_required", False)),
                    paywall=bool(source_config.get("paywall", False)),
                    store_full_text=bool(source_config.get("store_full_text", False)),
                    status=str(source_config.get("status", "active") or "active"),
                    owner=str(source_config.get("owner", "crawler") or "crawler"),
                )

                stats["processed_sources"] += 1
                stats["fetched_links"] += len(links)

                for i, result in enumerate(results):
                    if isinstance(result, Exception) or result is None:
                        logger.warning("Skip link due to crawl error: %s | error=%s", links[i], result)
                        continue

                    news_detail = result
                    if not news_detail.get("title"):
                        continue

                    raw_created, signal_created, _, skipped_duplicate = upsert_signal_from_news_detail(
                        db=db,
                        source=source,
                        source_url=links[i],
                        news_detail=news_detail,
                    )
                    stats["raw_items_created"] += 1 if raw_created else 0
                    stats["signals_created"] += 1 if signal_created else 0
                    stats["duplicates_skipped"] += 1 if skipped_duplicate else 0

                    saved_items.append(
                        {
                            "source": source_name,
                            "title": news_detail.get("title", ""),
                            "published_at": str(news_detail.get("published_at", "")),
                            "category": news_detail.get("category", ""),
                            "source_url": links[i],
                        }
                    )

        db.commit()

        published_count, enrichment_failures = process_pending_signal_enrichments(db=db, limit=500)
        db.commit()
        stats["signals_published"] = published_count
        stats["enrichment_failures"] = enrichment_failures

        logger.info("Crawler saved %s items", len(saved_items))
        logger.info("Crawler stats: %s", json.dumps(stats, ensure_ascii=False))
        logger.info("Crawler data: %s", json.dumps(saved_items, ensure_ascii=False))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
