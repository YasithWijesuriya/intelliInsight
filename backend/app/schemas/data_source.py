from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DataSourceCreate(BaseModel):
    # This is what the user SENDS when creating a data source
    name: str
    source_type: str
    url: Optional[str] = None  # only for Google Sheets

class DataSourceResponse(BaseModel):
    # This is what we SEND BACK to the user
    id: int
    name: str
    source_type: str
    file_size: Optional[int] = None
    row_count: Optional[int] = None
    columns: Optional[List[str]] = None
    is_processed: int
    created_at: datetime

    class Config:
        from_attributes = True
        # This tells Pydantic to read from SQLAlchemy model attributes
        # Without this, returning a SQLAlchemy object would fail