# PURPOSE: Stores user accounts for the platform
# COLUMNS: id, email, username, hashed_pw, is_active, is_admin, timestamps

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    # index=True creates a DB index → faster queries by id

    email      = Column(String, unique=True, nullable=False, index=True)
    # unique=True → no two users can have same email
    # nullable=False → this field is REQUIRED

    username   = Column(String, unique=True, nullable=False)
    hashed_pw  = Column(String, nullable=False)
    # NEVER store plain passwords — always hash them first

    is_active  = Column(Boolean, default=True)
    is_admin   = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # server_default=func.now() → DB sets this automatically on INSERT

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # onupdate=func.now() → DB updates this automatically on UPDATE