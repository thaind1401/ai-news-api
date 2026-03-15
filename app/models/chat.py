from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    timestamp: Optional[str] = None
