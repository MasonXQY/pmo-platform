from pydantic import BaseModel
from typing import Optional

class StandardResponse(BaseModel):
    request_id: str
    model: Optional[str]
    latency_ms: Optional[float]
    cost_estimate: Optional[float]
    output: Optional[str]
    error: Optional[str]
