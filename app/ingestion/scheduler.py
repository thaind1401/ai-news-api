from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import AppConfig
from app.ingestion.workers.pipeline import run_crawler, run_failed_enrichment_retry_job


def build_scheduler(config: AppConfig) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=config.timezone)
    scheduler.add_job(
        run_crawler,
        "interval",
        minutes=config.crawler_interval_minutes,
        id="signals_crawler",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.add_job(
        run_failed_enrichment_retry_job,
        "interval",
        minutes=config.enrichment_retry_interval_minutes,
        id="enrichment_retry_job",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    return scheduler
