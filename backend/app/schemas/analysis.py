from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class AnalysisResponse(BaseModel):
    id: int
    data_source_id: Optional[int] = None
    query_id: Optional[int] = None
    analysis_type: str
    agent_name: str
    result_json: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True