from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean
)
from sqlalchemy.sql import func

from app.db.db import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    todo = Column(String(500), nullable=False)
    completed = Column(Boolean, default=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    external_id = Column(Integer, unique=False, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
