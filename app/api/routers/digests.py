from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/api/v1/digest/today")
def get_today_digest():
    raise HTTPException(
        status_code=501,
        detail={"code": "NOT_IMPLEMENTED", "message": "Digest API is planned in next phase."},
    )
