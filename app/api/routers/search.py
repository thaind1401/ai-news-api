from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/api/v1/search")
def search_signals():
    raise HTTPException(
        status_code=501,
        detail={"code": "NOT_IMPLEMENTED", "message": "Search API is planned in next phase."},
    )
