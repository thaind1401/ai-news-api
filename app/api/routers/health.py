from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": "ai-signals-api", "time": datetime.now(timezone.utc).isoformat()}
