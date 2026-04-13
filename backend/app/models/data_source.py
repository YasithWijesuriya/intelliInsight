# PURPOSE: Tracks every uploaded file or Google Sheets link
# When a user uploads Excel, CSV, or connects Google Sheets → stored here

from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON
from sqlalchemy.sql import func
from database import Base
import enum

class SourceType(str, enum.Enum):
    # str enum = stored as string in DB ("excel", "csv", etc.)
    EXCEL         = "excel"
    CSV           = "csv"
    PDF           = "pdf"
    GOOGLE_SHEETS = "google_sheets"
    DATABASE      = "database"

class DataSource(Base):
    __tablename__ = "data_sources"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, nullable=True)
    # nullable=True → optional, we don't have auth yet

    name        = Column(String, nullable=False)
    # the original filename e.g. "Q3_Revenue.xlsx"

    source_type = Column(Enum(SourceType), nullable=False)
    # stored as "excel", "csv" etc. in the DB

    file_path   = Column(String, nullable=True)
    # local disk path e.g. "./uploads/structured/abc123_file.xlsx"

    url         = Column(String, nullable=True)
    # only for Google Sheets links

    file_size   = Column(Integer, nullable=True)
    # in bytes

    row_count   = Column(Integer, nullable=True)
    # filled in AFTER parsing the file

    columns     = Column(JSON, nullable=True)
    # JSON list of column names e.g. ["Revenue", "Cost", "Profit"]
    # JSON type lets you store lists/dicts directly in PostgreSQL

    is_processed = Column(Integer, default=0)
    # 0 = pending, 1 = done, 2 = error

    created_at  = Column(DateTime(timezone=True), server_default=func.now())