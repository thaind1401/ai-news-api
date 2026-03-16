from typing import Any

import httpx

from app.ingestion.workers.homepage_worker import discover_links_from_homepage_css
from app.ingestion.workers.rss_worker import discover_links_from_rss


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
        return await discover_links_from_homepage_css(
            client=client,
            url=str(discovery.get("url", "")).strip(),
            selector=str(discovery.get("selector", "")).strip(),
            limit=limit,
        )
    if method == "rss":
        return await discover_links_from_rss(
            client=client,
            url=str(discovery.get("url", "")).strip(),
            limit=limit,
        )
    return []
