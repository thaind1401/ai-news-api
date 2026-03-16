from pydantic import BaseModel


class DigestResponse(BaseModel):
    data: dict
