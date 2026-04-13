from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    summary: Optional[str] = None
    is_indexed: int
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentIndexRequest(BaseModel):
    # Sent when user wants to index a document into Pinecone
    document_id: int