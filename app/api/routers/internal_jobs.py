from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import load_dotenv_if_exists
from app.core.security import is_valid_internal_key, read_internal_api_key
from app.ingestion.workers.pipeline import run_crawler
from app.services.ingestion_service import run_enrichment_jobs
from app.services.signal_service import get_db

router = APIRouter()


def require_internal_key(x_internal_key: Optional[str] = Header(default=None, alias="X-Internal-Key")):
	if not read_internal_api_key():
		load_dotenv_if_exists()

	configured_key = read_internal_api_key()
	if not configured_key:
		raise HTTPException(
			status_code=503,
			detail={
				"code": "INTERNAL_API_KEY_NOT_CONFIGURED",
				"message": "Internal API is not configured. Set INTERNAL_API_KEY.",
			},
		)

	if not x_internal_key:
		raise HTTPException(
			status_code=401,
			detail={
				"code": "INTERNAL_API_KEY_REQUIRED",
				"message": "Missing X-Internal-Key header.",
			},
		)

	if not is_valid_internal_key(candidate=x_internal_key, expected=configured_key):
		raise HTTPException(
			status_code=403,
			detail={
				"code": "INTERNAL_API_KEY_INVALID",
				"message": "Invalid X-Internal-Key.",
			},
		)


@router.post("/api/internal/reingest")
async def reingest_now(_: None = Depends(require_internal_key)):
	await run_crawler()
	return {
		"status": "ok",
		"message": "Re-ingest completed.",
		"time": datetime.now(timezone.utc).isoformat(),
	}


@router.post("/api/internal/re-enrich")
def reenrich_now(
	pending_limit: int = Query(default=200, ge=0, le=2000),
	failed_retry_limit: int = Query(default=200, ge=0, le=2000),
	db: Session = Depends(get_db),
	_: None = Depends(require_internal_key),
):
	try:
		stats = run_enrichment_jobs(
			db=db,
			pending_limit=pending_limit,
			failed_retry_limit=failed_retry_limit,
		)
		db.commit()
		return {
			"status": "ok",
			"data": stats,
			"time": datetime.now(timezone.utc).isoformat(),
		}
	except Exception as exc:
		db.rollback()
		raise HTTPException(
			status_code=500,
			detail={
				"code": "INTERNAL_REENRICH_FAILED",
				"message": str(exc),
			},
		)


__all__ = ["router"]
