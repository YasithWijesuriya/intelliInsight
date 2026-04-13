# PURPOSE: Stores text chunks from documents
# After chunking a PDF, each chunk is stored as one row here

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class UnstructuredData(Base):
    __tablename__ = "unstructured_data"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False, index=True)
    # links back to the documents table

    chunk_index = Column(Integer, nullable=False)
    # which chunk number (0, 1, 2, ...)

    chunk_text  = Column(Text, nullable=False)
    # the actual text content of this chunk

    pinecone_id = Column(String, nullable=True)
    # the ID used in Pinecone e.g. "doc3_chunk7"
    
    last_accessed = Column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now()
    )

    created_at  = Column(DateTime(timezone=True), server_default=func.now())