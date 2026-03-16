from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ResponseMeta(BaseModel):
	server_time: datetime
	request_id: Optional[str] = None


class PaginationMeta(BaseModel):
	page: int
	size: int
	total: int
	total_pages: int
	has_next: bool


class ErrorPayload(BaseModel):
	code: str
	message: str
	details: Optional[dict] = None


class ErrorResponse(BaseModel):
	error: ErrorPayload


class SignalEnrichment(BaseModel):
	summary_one_line: Optional[str] = None
	summary_bullets: List[str] = Field(default_factory=list)
	why_it_matters: Optional[str] = None
	tags: List[str] = Field(default_factory=list)
	importance_score: Optional[int] = None
	confidence_score: Optional[float] = None


class SignalItem(BaseModel):
	id: int
	title: str
	source_url: str
	published_at: Optional[datetime] = None
	crawl_time: Optional[datetime] = None
	event_type: str
	source_name: Optional[str] = None
	company_name: Optional[str] = None
	topic_name: Optional[str] = None
	raw_excerpt: Optional[str] = None
	author_name: Optional[str] = None
	image_url: Optional[str] = None
	enrichment: Optional[SignalEnrichment] = None


class SignalListResponse(BaseModel):
	data: List[SignalItem]
	pagination: PaginationMeta
	meta: ResponseMeta


class SignalDetailResponse(BaseModel):
	data: SignalItem
	meta: ResponseMeta


class TopicsResponse(BaseModel):
	data: List[str]
	meta: ResponseMeta


class CompaniesResponse(BaseModel):
	data: List[str]
	meta: ResponseMeta


__all__ = [
	"SignalEnrichment",
	"SignalItem",
	"SignalListResponse",
	"SignalDetailResponse",
	"TopicsResponse",
	"CompaniesResponse",
	"ErrorResponse",
]
