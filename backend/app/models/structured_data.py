# PURPOSE: Stores parsed rows from Excel/CSV files
# Think of this as a flexible row store — each row becomes a JSON record

from sqlalchemy import Column, Integer, DateTime, JSON
from sqlalchemy.sql import func
from database import Base

class StructuredData(Base):
    __tablename__ = "structured_data"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, nullable=False, index=True)
    # links back to the data_sources table

    row_index = Column(Integer, nullable=False)
    # which row number this was in the original file

    row_data = Column(JSON, nullable=False)
    # the actual row as JSON e.g. {"Revenue": 50000, "Cost": 30000, "Date": "2024-01"}

    last_accessed = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    created_at     = Column(DateTime(timezone=True), server_default=func.now())