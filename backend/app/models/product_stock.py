# PURPOSE: Stores inventory/stock data rows
# Used by inventory_agents for stock monitoring and alerts

from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from app.database import Base

class ProductStock(Base):
    __tablename__ = "product_stock"

    id           = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    product_code = Column(String, nullable=True, index=True)
    category     = Column(String, nullable=True)

    quantity     = Column(Float, nullable=False, default=0)
    unit_price   = Column(Float, nullable=True)
    reorder_level= Column(Float, nullable=True, default=50)
    # if quantity drops below reorder_level → send alert

    supplier     = Column(String, nullable=True)
    location     = Column(String, nullable=True)
    notes        = Column(Text, nullable=True)

    data_source_id = Column(Integer, nullable=True)
    # which uploaded file this came from

    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now())