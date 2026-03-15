from  fastapi import APIRouter
from app.models.chat import ChatRequest

router = APIRouter()

@router.post("/chat")
def chat(req: ChatRequest):
    return {
        "data": f"You said: {req.message}"
    }