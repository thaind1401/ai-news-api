import asyncio
import logging
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.ingestion.parsers.news_parser import crawl_news
from app.ingestion.workers.source_discovery import discover_source_links
from app.ingestion.workers.types import SourceIngestionResult
from app.services.ingestion_service import (
    finish_source_fetch_run,
    get_or_create_source,
    start_source_fetch_run,
    upsert_signal_from_news_detail,
)

logger = logging.getLogger(__name__)


async def run_source_ingestion(
    client: httpx.AsyncClient,
    db: Session,
    source_config: dict[str, Any],
) -> SourceIngestionResult:
    source_name = str(source_config.get("name", "")).strip()
    result = SourceIngestionResult(source_name=source_name)
    if not source_name:
        return result

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

    fetch_run = start_source_fetch_run(
        db=db,
        source_id=source.id,
        run_metadata={
            "source": source_name,
            "discovery_type": str((source_config.get("discovery") or {}).get("type", "")),
        },
    )

    source_links: list[str] = []

    try:
        source_links = await discover_source_links(client=client, source_config=source_config)
        result.links_discovered = len(source_links)
        if not source_links:
            logger.info("No links discovered for source=%s", source_name)

        detail_parser = str(source_config.get("detail_parser", "generic_meta") or "generic_meta")
        crawl_results = await asyncio.gather(
            *(crawl_news(link, parser_type=detail_parser) for link in source_links),
            return_exceptions=True,
        )

        for index, crawl_result in enumerate(crawl_results):
            source_url = source_links[index]
            if isinstance(crawl_result, Exception) or crawl_result is None:
                logger.warning("Skip link due to crawl error: %s | error=%s", source_url, crawl_result)
                result.crawl_errors += 1
                continue

            news_detail = crawl_result
            if not news_detail.get("title"):
                result.crawl_errors += 1
                continue

            raw_created, signal_created, _, skipped_duplicate = upsert_signal_from_news_detail(
                db=db,
                source=source,
                source_url=source_url,
                news_detail=news_detail,
                fetch_run_id=fetch_run.id,
            )
            result.raw_items_created += 1 if raw_created else 0
            result.signals_created += 1 if signal_created else 0
            result.duplicates_skipped += 1 if skipped_duplicate else 0

            result.saved_items.append(
                {
                    "source": source_name,
                    "title": news_detail.get("title", ""),
                    "published_at": str(news_detail.get("published_at", "")),
                    "category": news_detail.get("category", ""),
                    "source_url": source_url,
                }
            )

        finish_source_fetch_run(
            fetch_run=fetch_run,
            status="success",
            items_fetched=result.links_discovered,
            items_created=result.raw_items_created,
            run_metadata={
                "links_discovered": result.links_discovered,
                "signals_created": result.signals_created,
                "duplicates_skipped": result.duplicates_skipped,
                "crawl_errors": result.crawl_errors,
            },
        )
    except Exception as exc:
        result.crawl_errors += 1
        logger.warning("Source run failed source=%s error=%s", source_name, exc)
        finish_source_fetch_run(
            fetch_run=fetch_run,
            status="failed",
            items_fetched=result.links_discovered,
            items_created=result.raw_items_created,
            error_message=str(exc),
            run_metadata={
                "links_discovered": result.links_discovered,
                "signals_created": result.signals_created,
                "duplicates_skipped": result.duplicates_skipped,
                "crawl_errors": result.crawl_errors,
            },
        )

    return result
