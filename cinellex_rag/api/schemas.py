from pydantic import BaseModel
from typing import Optional, Dict, Any


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    route: str
    source: str
    metadata: Optional[Dict[str, Any]] = {}