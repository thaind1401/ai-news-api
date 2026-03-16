from datetime import datetime, timezone
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.schemas.signal import (
	CompaniesResponse,
	ErrorResponse,
	SignalDetailResponse,
	SignalListResponse,
	TopicsResponse,
)
from app.services.signal_service import (
	get_db,
	get_signal_by_id,
	list_companies,
	list_signals,
	list_topics,
	list_trending_signals,
)

router = APIRouter()


def _build_meta(request: Request):
	return {
		"server_time": datetime.now(timezone.utc),
		"request_id": request.headers.get("x-request-id"),
	}


def _to_signal_item(signal):
	enrichment = signal.ai_enrichment
	return {
		"id": signal.id,
		"title": signal.title,
		"source_url": signal.source_url,
		"published_at": signal.published_at,
		"crawl_time": signal.crawl_time,
		"event_type": signal.event_type,
		"source_name": signal.source.name if signal.source else None,
		"company_name": signal.company.name if signal.company else None,
		"topic_name": signal.primary_topic.name if signal.primary_topic else None,
		"raw_excerpt": signal.raw_excerpt,
		"author_name": signal.author_name,
		"image_url": signal.image_url,
		"enrichment": {
			"summary_one_line": enrichment.summary_one_line if enrichment else None,
			"summary_bullets": enrichment.summary_bullets if enrichment and enrichment.summary_bullets else [],
			"why_it_matters": enrichment.why_it_matters if enrichment else None,
			"tags": enrichment.tags if enrichment and enrichment.tags else [],
			"importance_score": enrichment.importance_score if enrichment else None,
			"confidence_score": float(enrichment.confidence_score) if enrichment and enrichment.confidence_score is not None else None,
		}
		if enrichment
		else None,
	}


@router.get(
	"/api/v1/signals",
	response_model=SignalListResponse,
	responses={422: {"model": ErrorResponse}},
)
def get_signals(
	request: Request,
	page: int = Query(default=1, ge=1),
	size: int = Query(default=10, ge=1, le=100),
	q: Optional[str] = Query(default=None),
	source: Optional[str] = Query(default=None),
	company: Optional[str] = Query(default=None),
	topic: Optional[str] = Query(default=None),
	event_type: Optional[str] = Query(default=None),
	from_date: Optional[datetime] = Query(default=None, alias="from"),
	to_date: Optional[datetime] = Query(default=None, alias="to"),
	sort: Literal["newest", "oldest"] = Query(default="newest"),
	db: Session = Depends(get_db),
):
	if from_date and to_date and from_date > to_date:
		raise HTTPException(
			status_code=422,
			detail={
				"code": "INVALID_DATE_RANGE",
				"message": "`from` must be less than or equal to `to`.",
			},
		)

	rows, total = list_signals(
		db=db,
		page=page,
		size=size,
		query_text=q,
		source=source,
		company=company,
		topic=topic,
		event_type=event_type,
		from_date=from_date,
		to_date=to_date,
		sort=sort,
	)

	items = [_to_signal_item(item) for item in rows]
	total_pages = max(1, (total + size - 1) // size)

	return {
		"data": items,
		"pagination": {
			"page": page,
			"size": size,
			"total": total,
			"total_pages": total_pages,
			"has_next": page < total_pages,
		},
		"meta": _build_meta(request),
	}


@router.get(
	"/api/v1/signals/trending",
	response_model=SignalListResponse,
)
def get_trending_signals(
	request: Request,
	limit: int = Query(default=10, ge=1, le=50),
	within_hours: int = Query(default=24, ge=1, le=168),
	db: Session = Depends(get_db),
):
	rows = list_trending_signals(db=db, limit=limit, within_hours=within_hours)
	items = [_to_signal_item(item) for item in rows]
	total = len(items)

	return {
		"data": items,
		"pagination": {
			"page": 1,
			"size": limit,
			"total": total,
			"total_pages": 1,
			"has_next": False,
		},
		"meta": _build_meta(request),
	}


@router.get(
	"/api/v1/topics",
	response_model=TopicsResponse,
)
def get_topics(request: Request, db: Session = Depends(get_db)):
	rows = list_topics(db)
	return {"data": rows, "meta": _build_meta(request)}


@router.get(
	"/api/v1/companies",
	response_model=CompaniesResponse,
)
def get_companies(request: Request, db: Session = Depends(get_db)):
	rows = list_companies(db)
	return {"data": rows, "meta": _build_meta(request)}


@router.get(
	"/api/v1/signals/{signal_id}",
	response_model=SignalDetailResponse,
	responses={404: {"model": ErrorResponse}},
)
def get_signal_detail(signal_id: int, request: Request, db: Session = Depends(get_db)):
	item = get_signal_by_id(db, signal_id)
	if not item:
		raise HTTPException(
			status_code=404,
			detail={"code": "SIGNAL_NOT_FOUND", "message": "Signal not found."},
		)

	return {"data": _to_signal_item(item), "meta": _build_meta(request)}


__all__ = ["router"]
