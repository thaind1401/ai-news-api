from pydantic import BaseModel


class SearchResponse(BaseModel):
    data: list[dict]
