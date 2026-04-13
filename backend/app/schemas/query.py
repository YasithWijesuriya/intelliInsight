from typing import List 
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QueryRequest(BaseModel):
    # What the frontend sends when the user asks a question
    query: str
    data_source_id: Optional[int] = None
    # If user wants to ask about a specific uploaded file

    document_id: Optional[int] = None
    # If user wants to ask about a specific document

class QueryResponse(BaseModel):
    # What we send back after the AI processes the query
    id: int
    user_query: str
    query_type: Optional[str] = None
    response: Optional[str] = None
    sources_used: Optional[str] = None
    confidence: Optional[float] = None
    exec_time_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class QuickQueryResponse(BaseModel):
    # A simpler response for streaming / quick answers
    query_type: str
    answer: str
    confidence: float
    agents_used: List[str]
    execution_time_ms: int
