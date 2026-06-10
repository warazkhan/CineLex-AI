from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    route: str
    source: str
    movies: List[Dict[str, Any]] = []
    metadata: Optional[Dict[str, Any]] = {}