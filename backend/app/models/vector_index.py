# PURPOSE: Tracks which documents have been indexed in Pinecone
# Prevents duplicate indexing and helps with re-indexing

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

class VectorIndex(Base):
    __tablename__ = "vector_indices"

    id          = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False, index=True)
    pinecone_id = Column(String, nullable=False)
    # the Pinecone vector ID e.g. "doc5_chunk12"

    chunk_index = Column(Integer, nullable=False)
    chunk_text  = Column(String, nullable=True)

    is_active   = Column(Boolean, default=True)
    
    last_accessed = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    created_at  = Column(DateTime(timezone=True), server_default=func.now())