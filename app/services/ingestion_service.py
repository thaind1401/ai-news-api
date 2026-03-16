import hashlib
import re
import unicodedata
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Optional, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database.models import Company, RawItem, Signal, SignalAIEnrichment, Source, Topic

DEFAULT_EVENT_TYPE = "market_move"
TITLE_SIMILARITY_THRESHOLD = 0.93
COMPANY_EVENT_SIMILARITY_THRESHOLD = 0.88


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    if slug:
        return slug
    digest = hashlib.md5(text.encode("utf-8")).hexdigest()[:8]
    return f"topic-{digest}"


def normalize_text(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    lower = ascii_text.lower()
    normalized = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", lower)).strip()
    return normalized


def similarity_ratio(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, normalize_text(left), normalize_text(right)).ratio()


def build_summary(news_detail: dict) -> str:
    for value in [
        news_detail.get("sub_title"),
        news_detail.get("description"),
        news_detail.get("title"),
    ]:
        if value and str(value).strip():
            text = str(value).strip()
            if len(text) <= 280:
                return text
            return f"{text[:277]}..."
    return ""


def guess_company_name(news_detail: dict) -> Optional[str]:
    explicit = news_detail.get("company_name")
    if explicit and str(explicit).strip():
        return str(explicit).strip()

    combined = " ".join(
        [
            str(news_detail.get("title") or ""),
            str(news_detail.get("sub_title") or ""),
            str(news_detail.get("description") or ""),
        ]
    )
    pattern = r"(?:Công ty|Tập đoàn|Doanh nghiệp)\s+([A-ZÀ-Ỹ][\wÀ-ỹ&\-. ]{1,80})"
    match = re.search(pattern, combined)
    if not match:
        return None

    candidate = match.group(1).strip(" .,-")
    if len(candidate) < 2:
        return None
    return candidate[:120]


def get_or_create_source(db: Session, name: str, base_url: str, source_type: str = "news_site") -> Source:
    source = db.query(Source).filter(Source.name == name).first()
    if source:
        return source

    source = Source(
        name=name,
        source_type=source_type,
        base_url=base_url,
        ingest_method="html",
        risk_level="A",
        terms_reviewed=True,
        robots_reviewed=True,
        auth_required=False,
        paywall=False,
        store_full_text=False,
        status="active",
        owner="crawler",
    )
    db.add(source)
    db.flush()
    return source


def get_or_create_topic(db: Session, category: Optional[str]) -> Optional[Topic]:
    if not category or not category.strip():
        return None

    cleaned = category.strip()
    by_name = db.query(Topic).filter(Topic.name == cleaned).first()
    if by_name:
        return by_name

    slug = slugify(cleaned)
    by_slug = db.query(Topic).filter(Topic.slug == slug).first()
    if by_slug:
        return by_slug

    topic = Topic(name=cleaned, slug=slug)
    db.add(topic)
    db.flush()
    return topic


def get_or_create_company(db: Session, company_name: Optional[str]) -> Optional[Company]:
    if not company_name or not company_name.strip():
        return None

    cleaned = company_name.strip()
    normalized_name = normalize_text(cleaned)
    if not normalized_name:
        return None

    company = db.query(Company).filter(Company.normalized_name == normalized_name).first()
    if company:
        return company

    company = Company(name=cleaned, normalized_name=normalized_name)
    db.add(company)
    db.flush()
    return company


def find_title_similarity_duplicate(
    db: Session,
    source_id: int,
    title: str,
    exclude_signal_id: Optional[int] = None,
) -> Optional[Tuple[Signal, float]]:
    if not title or not title.strip():
        return None

    query = (
        db.query(Signal)
        .filter(Signal.source_id == source_id)
        .order_by(desc(Signal.published_at), desc(Signal.id))
    )
    if exclude_signal_id is not None:
        query = query.filter(Signal.id != exclude_signal_id)

    best_signal = None
    best_score = 0.0
    for candidate in query.limit(200).all():
        score = similarity_ratio(title, candidate.title or "")
        if score > best_score:
            best_signal = candidate
            best_score = score

    if best_signal and best_score >= TITLE_SIMILARITY_THRESHOLD:
        return best_signal, best_score
    return None


def find_company_event_duplicate(
    db: Session,
    company_id: Optional[int],
    event_type: str,
    title: str,
    exclude_signal_id: Optional[int] = None,
) -> Optional[Tuple[Signal, float]]:
    if not company_id:
        return None

    query = (
        db.query(Signal)
        .filter(Signal.company_id == company_id, Signal.event_type == event_type)
        .order_by(desc(Signal.published_at), desc(Signal.id))
    )
    if exclude_signal_id is not None:
        query = query.filter(Signal.id != exclude_signal_id)

    best_signal = None
    best_score = 0.0
    for candidate in query.limit(200).all():
        score = similarity_ratio(title, candidate.title or "")
        if score > best_score:
            best_signal = candidate
            best_score = score

    if best_signal and best_score >= COMPANY_EVENT_SIMILARITY_THRESHOLD:
        return best_signal, best_score
    return None


def upsert_signal_from_news_detail(
    db: Session,
    source: Source,
    source_url: str,
    news_detail: dict,
):
    now = datetime.now(timezone.utc)
    title = news_detail.get("title", "")
    sub_title = news_detail.get("sub_title", "")
    description = news_detail.get("description", "")
    author = news_detail.get("author", "")
    category = news_detail.get("category", "")
    image = news_detail.get("image", "")
    published_at = news_detail.get("published_at")

    payload = {
        "source": source.name,
        "source_url": source_url,
        "title": title,
        "sub_title": sub_title,
        "image": image,
        "description": description,
        "author": author,
        "category": category,
        "published_at": published_at.isoformat() if published_at else None,
    }

    raw_item = (
        db.query(RawItem)
        .filter(RawItem.source_id == source.id, RawItem.source_url == source_url)
        .first()
    )
    raw_created = False
    if not raw_item:
        raw_item = RawItem(
            source_id=source.id,
            source_url=source_url,
            title=title,
            published_at=published_at,
            raw_payload=payload,
            parse_status="parsed",
            fetched_at=now,
        )
        db.add(raw_item)
        db.flush()
        raw_created = True
    else:
        raw_item.title = title
        raw_item.published_at = published_at
        raw_item.raw_payload = payload
        raw_item.parse_status = "parsed"
        raw_item.parse_error = None
        raw_item.fetched_at = now

    topic = get_or_create_topic(db, category)
    company = get_or_create_company(db, guess_company_name(news_detail))

    signal = db.query(Signal).filter(Signal.raw_item_id == raw_item.id).first()
    signal_created = False
    signal_skipped_as_duplicate = False

    if not signal:
        title_dup = find_title_similarity_duplicate(db, source.id, title)
        company_event_dup = find_company_event_duplicate(
            db,
            company.id if company else None,
            DEFAULT_EVENT_TYPE,
            title,
        )

        duplicate_target = title_dup or company_event_dup
        if duplicate_target:
            raw_item.raw_payload = {
                **raw_item.raw_payload,
                "dedupe": {
                    "duplicate_signal_id": duplicate_target[0].id,
                    "similarity": round(duplicate_target[1], 4),
                    "mode": "title_similarity" if title_dup else "company_event",
                },
            }
            signal_skipped_as_duplicate = True
        else:
            dedup_key = f"{source.name}:{source_url}"
            signal = Signal(
                source_id=source.id,
                raw_item_id=raw_item.id,
                source_url=source_url,
                title=title,
                raw_excerpt=sub_title or description,
                author_name=author,
                image_url=image,
                published_at=published_at,
                crawl_time=now,
                company_id=company.id if company else None,
                primary_topic_id=topic.id if topic else None,
                event_type=DEFAULT_EVENT_TYPE,
                dedup_key=dedup_key,
                signal_status="active",
                visibility="public",
            )
            db.add(signal)
            db.flush()
            signal_created = True
    else:
        signal.title = title
        signal.raw_excerpt = sub_title or description
        signal.author_name = author
        signal.image_url = image
        signal.published_at = published_at
        signal.crawl_time = now
        signal.company_id = company.id if company else None
        signal.primary_topic_id = topic.id if topic else None
        signal.event_type = DEFAULT_EVENT_TYPE
        signal.signal_status = "active"
        signal.visibility = "public"

    enrichment_created = False
    if signal:
        summary = build_summary(news_detail)
        enrichment = (
            db.query(SignalAIEnrichment)
            .filter(SignalAIEnrichment.signal_id == signal.id)
            .first()
        )
        if not enrichment:
            enrichment = SignalAIEnrichment(
                signal_id=signal.id,
                summary_one_line=summary,
                summary_bullets=[sub_title] if sub_title else [],
                why_it_matters=summary,
                tags=[category] if category else [],
                importance_score=3,
                confidence_score=1,
                company_name_extracted=company.name if company else None,
                topic_extracted=category,
                event_type_extracted=DEFAULT_EVENT_TYPE,
                model_name="rule-based-v1",
                prompt_version="baseline-v2",
                enrichment_status="done",
            )
            db.add(enrichment)
            enrichment_created = True
        else:
            enrichment.summary_one_line = summary
            enrichment.summary_bullets = [sub_title] if sub_title else []
            enrichment.why_it_matters = summary
            enrichment.tags = [category] if category else []
            enrichment.importance_score = 3
            enrichment.confidence_score = 1
            enrichment.company_name_extracted = company.name if company else None
            enrichment.topic_extracted = category
            enrichment.event_type_extracted = DEFAULT_EVENT_TYPE
            enrichment.model_name = "rule-based-v1"
            enrichment.prompt_version = "baseline-v2"
            enrichment.enrichment_status = "done"

    return raw_created, signal_created, enrichment_created, signal_skipped_as_duplicate