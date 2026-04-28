# PURPOSE: Stores metadata for uploaded PDFs and documents
# The actual text content is stored in unstructured_data.py (as chunks)

from sqlalchemy import Column, Integer, String, DateTime, Text, Float,literal
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped,mapped_column
from app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id         = Column(Integer, primary_key=True, index=True)
    filename   = Column(String, nullable=False)
    file_path  = Column(String, nullable=False)
    file_type  = Column(String, nullable=False)
    # "pdf", "docx", "txt"

    file_size  = Column(Integer, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)


    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)    
    # Text = unlimited length string (unlike String which has a limit)
    # stores the FULL extracted text from the document

    summary    = Column(Text, nullable=True)
    # AI-generated summary — filled in after processing

    is_indexed: Mapped[int] = mapped_column(Integer, default=0)
    # 0 = not in Pinecone yet, 1 = indexed, 2 = error

    last_accessed = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # optional soft delete (safer than hard delete)
    is_deleted = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

