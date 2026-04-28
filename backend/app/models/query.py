# PURPOSE: Logs every query a user asks + the AI's answer
# Important for: history, debugging, analytics

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class QueryType(str, enum.Enum):
    FINANCIAL   = "financial"
    DOCUMENT    = "document"
    ADVISORY    = "advisory"
    COMPARATIVE = "comparative"
    HYBRID      = "hybrid"

class Query(Base):
    __tablename__ = "queries"

    id           = Column(Integer, primary_key=True, index=True)
    user_query   = Column(Text, nullable=False)
    # exactly what the user typed

    query_type   = Column(Enum(QueryType), nullable=True)
    # classified by the AI: financial/document/advisory/hybrid

    reWriten_query = Column(Text, nullable=True)
    # after rewriting for clarity/consistency

    response     = Column(Text, nullable=True)
    # the final AI-generated answer

    sources_used = Column(String, nullable=True)
    # which agents ran e.g. "TrendAgent,AnomalyAgent,KPIEngine"

    confidence   = Column(Float, nullable=True)
    # 0.0 to 1.0 — how confident the AI is

    exec_time_ms = Column(Integer, nullable=True)
    # how long it took in milliseconds

    created_at   = Column(DateTime(timezone=True), server_default=func.now())