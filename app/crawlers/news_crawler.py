import asyncio
from datetime import datetime
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


async def crawl_news(url: str) -> dict:
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=REQUEST_HEADERS) as client:
        response = await _get_with_retry(client, url)

    soup = BeautifulSoup(response.content, "html.parser")

    # Lấy title
    title = soup.find("h1", class_="title-detail")
    title = title.text.strip() if title else ""

    # Lấy sub_title
    sub_title = soup.find("p", class_="description")
    sub_title = sub_title.text.strip() if sub_title else ""

    # Lấy image
    image_tag = soup.find("figure", class_="fig-picture")
    image = ""
    if image_tag and image_tag.img:
        image = image_tag.img.get("data-src") or image_tag.img.get("src") or ""

    # Lấy description (nội dung đầu tiên)
    description = ""
    content = soup.find("article", class_="fck_detail")
    if content:
        first_p = content.find("p")
        description = first_p.text.strip() if first_p else ""

    # Lấy author
    author = ""
    author_tag = soup.find("p", class_="author_mail")
    if author_tag:
        author = author_tag.text.strip()
    else:
        # Thường author nằm ở cuối bài viết
        author_candidates = content.find_all("strong") if content else []
        if author_candidates:
            author = author_candidates[-1].text.strip()

    # Lấy published_at
    published_at = None
    time_tag = soup.find("span", class_="date")
    if time_tag:
        published_text = time_tag.text.strip()
        # Chuyển về ISO format nếu cần
        try:
            published_at = datetime.strptime(published_text, "%d/%m/%Y, %H:%M (GMT+7)")
        except Exception:
            try:
                # Một số bài có tiền tố thứ trong tuần: "Thứ hai, 11/03/2026, 08:22 (GMT+7)"
                date_part = published_text.split(", ", 1)[1]
                published_at = datetime.strptime(date_part, "%d/%m/%Y, %H:%M (GMT+7)")
            except Exception:
                published_at = None

    # Lấy category
    category = ""
    breadcrumb = soup.find("ul", class_="breadcrumb")
    if breadcrumb:
        items = breadcrumb.find_all("li")
        if len(items) > 1:
            category = items[1].text.strip()

        output = {
            "title": title,
            "sub_title": sub_title,
            "image": image,
            "description": description,
            "author": author,
            "published_at": published_at,
            "category": category,
        }

        # Không trả về url hoặc source nữa
        output.pop("url", None)
        output.pop("source", None)

        return output