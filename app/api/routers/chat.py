from fastapi import APIRouter

from app.schemas.chat import ChatRequest

router = APIRouter()


@router.post("/api/v1/chat")
def chat(req: ChatRequest):
	return {
		"data": f"You said: {req.message}"
	}


__all__ = ["router"]
