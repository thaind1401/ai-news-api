from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/api/v1/me")
def get_me():
    raise HTTPException(
        status_code=501,
        detail={"code": "NOT_IMPLEMENTED", "message": "User API is planned in next phase."},
    )
