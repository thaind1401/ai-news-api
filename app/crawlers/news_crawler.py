import asyncio
from datetime import datetime
from email.utils import parsedate_to_datetime
import logging

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


async def _get_with_retry(client: httpx.AsyncClient, url: str, retries: int = 3) -> httpx.Response:
    for attempt in range(1, retries + 1):
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response
        except Exception as exc:
            if attempt == retries:
                raise
            backoff = 0.5 * attempt
            logger.warning("Request failed (%s), retrying in %.1fs: %s", attempt, backoff, exc)
            await asyncio.sleep(backoff)


def _parse_datetime(value: str | None):
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None

    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        pass

    try:
        return parsedate_to_datetime(text)
    except Exception:
        pass

    for fmt in [
        "%d/%m/%Y, %H:%M (GMT+7)",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
    ]:
        try:
            return datetime.strptime(text, fmt)
        except Exception:
            continue
    return None


def _extract_meta(soup: BeautifulSoup, keys: list[str]) -> str:
    lowered = {key.lower() for key in keys}
    for tag in soup.find_all("meta"):
        key = str(tag.get("property") or tag.get("name") or tag.get("itemprop") or "").strip().lower()
        if key in lowered:
            content = str(tag.get("content") or "").strip()
            if content:
                return content
    return ""


def _parse_vnexpress(soup: BeautifulSoup) -> dict:
    title_tag = soup.find("h1", class_="title-detail")
    title = title_tag.text.strip() if title_tag else ""

    sub_title_tag = soup.find("p", class_="description")
    sub_title = sub_title_tag.text.strip() if sub_title_tag else ""

    image_tag = soup.find("figure", class_="fig-picture")
    image = ""
    if image_tag and image_tag.img:
        image = image_tag.img.get("data-src") or image_tag.img.get("src") or ""

    description = ""
    content = soup.find("article", class_="fck_detail")
    if content:
        first_p = content.find("p")
        description = first_p.text.strip() if first_p else ""

    author = ""
    author_tag = soup.find("p", class_="author_mail")
    if author_tag:
        author = author_tag.text.strip()
    else:
        author_candidates = content.find_all("strong") if content else []
        if author_candidates:
            author = author_candidates[-1].text.strip()

    published_at = None
    time_tag = soup.find("span", class_="date")
    if time_tag:
        published_text = time_tag.text.strip()
        published_at = _parse_datetime(published_text)
        if published_at is None and ", " in published_text:
            try:
                date_part = published_text.split(", ", 1)[1]
                published_at = _parse_datetime(date_part)
            except Exception:
                published_at = None

    category = ""
    breadcrumb = soup.find("ul", class_="breadcrumb")
    if breadcrumb:
        items = breadcrumb.find_all("li")
        if len(items) > 1:
            category = items[1].text.strip()

    return {
        "title": title,
        "sub_title": sub_title,
        "image": image,
        "description": description,
        "author": author,
        "published_at": published_at,
        "category": category,
    }


def _parse_generic(soup: BeautifulSoup) -> dict:
    title = _extract_meta(soup, ["og:title", "twitter:title"]).strip()
    if not title:
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else ""
    if not title:
        page_title = soup.find("title")
        title = page_title.get_text(strip=True) if page_title else ""

    sub_title = _extract_meta(soup, ["description", "og:description", "twitter:description"]).strip()

    image = _extract_meta(soup, ["og:image", "twitter:image"]).strip()

    description = ""
    article = soup.find("article")
    if article:
        p = article.find("p")
        description = p.get_text(strip=True) if p else ""
    if not description:
        p = soup.find("p")
        description = p.get_text(strip=True) if p else ""
    if not description:
        description = sub_title

    author = _extract_meta(soup, ["author", "article:author"]).strip()
    if not author:
        author_tag = soup.select_one("[rel='author'], .author, .byline")
        author = author_tag.get_text(strip=True) if author_tag else ""

    published_raw = _extract_meta(
        soup,
        [
            "article:published_time",
            "date",
            "pubdate",
            "publishdate",
            "datepublished",
        ],
    )
    if not published_raw:
        time_tag = soup.find("time")
        if time_tag:
            published_raw = str(time_tag.get("datetime") or time_tag.get_text(strip=True)).strip()
    published_at = _parse_datetime(published_raw)

    category = _extract_meta(soup, ["article:section", "section"]).strip()

    return {
        "title": title,
        "sub_title": sub_title,
        "image": image,
        "description": description,
        "author": author,
        "published_at": published_at,
        "category": category,
    }


async def crawl_news(url: str, parser_type: str = "generic_meta") -> dict:
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=REQUEST_HEADERS) as client:
        response = await _get_with_retry(client, url)

    soup = BeautifulSoup(response.content, "html.parser")
    if parser_type == "vnexpress":
        return _parse_vnexpress(soup)
    return _parse_generic(soup)