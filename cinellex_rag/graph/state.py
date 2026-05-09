from typing import TypedDict, Any, Optional, Dict


class GraphState(TypedDict):
    query: str
    route: str        
    result: Any
    metadata: Optional[Dict]