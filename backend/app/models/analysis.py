# PURPOSE: Stores results from each AI agent run
# When TrendAgent analyses a file, the result is stored here

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float
from sqlalchemy.sql import func
from app.database import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id             = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, nullable=True)
    query_id       = Column(Integer, nullable=True)

    analysis_type  = Column(String, nullable=False)
    # "trend", "anomaly", "kpi", "financial", "advisory"

    agent_name     = Column(String, nullable=False)
    # "TrendAgent", "AnomalyAgent", "KPIEngine" etc.

    result_json    = Column(JSON, nullable=True)
    # full structured result as JSON — can be charts data, tables, etc.

    summary        = Column(Text, nullable=True)
    # human-readable summary of the result

    confidence     = Column(Float, nullable=True)

    created_at     = Column(DateTime(timezone=True), server_default=func.now())