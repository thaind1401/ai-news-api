from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
	message: str
	user_id: Optional[str] = None
	timestamp: Optional[str] = None


__all__ = ["ChatRequest"]
