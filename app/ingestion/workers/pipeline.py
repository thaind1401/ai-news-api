import json
import logging

import httpx

from app.database.db import SessionLocal
from app.ingestion.sources.registry import load_source_registry
from app.ingestion.workers.source_worker import run_source_ingestion
from app.services.ingestion_service import run_enrichment_jobs

logger = logging.getLogger(__name__)

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


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
        "enrichment_retry_success": 0,
        "enrichment_retry_failures": 0,
        "duplicates_skipped": 0,
    }

    db = SessionLocal()
    saved_items = []
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=REQUEST_HEADERS) as client:
            for source_config in source_configs:
                ingestion_result = await run_source_ingestion(
                    client=client,
                    db=db,
                    source_config=source_config,
                )
                if not ingestion_result.source_name:
                    continue

                stats["processed_sources"] += 1
                stats["fetched_links"] += ingestion_result.links_discovered
                stats["raw_items_created"] += ingestion_result.raw_items_created
                stats["signals_created"] += ingestion_result.signals_created
                stats["duplicates_skipped"] += ingestion_result.duplicates_skipped
                saved_items.extend(ingestion_result.saved_items)

        db.commit()

        enrichment_stats = run_enrichment_jobs(
            db=db,
            pending_limit=500,
            failed_retry_limit=200,
        )
        db.commit()
        stats["signals_published"] = enrichment_stats["published_total"]
        stats["enrichment_failures"] = enrichment_stats["failed_total"]
        stats["enrichment_retry_success"] = enrichment_stats["retry_success"]
        stats["enrichment_retry_failures"] = enrichment_stats["retry_failed"]

        logger.info("Crawler saved %s items", len(saved_items))
        logger.info("Crawler stats: %s", json.dumps(stats, ensure_ascii=False))
        logger.info("Crawler data: %s", json.dumps(saved_items, ensure_ascii=False))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def run_failed_enrichment_retry_job(limit: int = 200) -> dict[str, int]:
    db = SessionLocal()
    try:
        enrichment_stats = run_enrichment_jobs(
            db=db,
            pending_limit=0,
            failed_retry_limit=limit,
        )
        db.commit()
        return enrichment_stats
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
