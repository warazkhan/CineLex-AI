from typing import TypedDict, Any, Optional, Dict


class GraphState(TypedDict):
    query: str
    route: str
    result: Dict[str, Any]   # IMPORTANT: ALWAYS DICT
    metadata: Optional[Dict]