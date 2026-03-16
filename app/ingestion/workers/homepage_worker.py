from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup


async def discover_links_from_homepage_css(
    client: httpx.AsyncClient,
    url: str,
    selector: str,
    limit: int,
) -> list[str]:
    source_url = str(url or "").strip()
    css_selector = str(selector or "").strip()
    if not source_url or not css_selector:
        return []

    response = await client.get(source_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    links: list[str] = []
    for anchor in soup.select(css_selector):
        link = str(anchor.get("href", "")).strip()
        if not link:
            continue

        absolute_link = urljoin(source_url, link)
        if not absolute_link.startswith("http"):
            continue

        if absolute_link not in links:
            links.append(absolute_link)
        if len(links) >= limit:
            break

    return links
