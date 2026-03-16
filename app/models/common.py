from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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
