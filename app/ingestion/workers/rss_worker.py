import xml.etree.ElementTree as ET

import httpx


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
        return _text_or_none(entry.findtext("link"))

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


async def discover_links_from_rss(
    client: httpx.AsyncClient,
    url: str,
    limit: int,
) -> list[str]:
    source_url = str(url or "").strip()
    if not source_url:
        return []

    response = await client.get(source_url)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    links: list[str] = []
    for entry in _iter_entries(root):
        link = _extract_link_from_entry(entry)
        if link and link not in links:
            links.append(link)
        if len(links) >= limit:
            break

    return links
