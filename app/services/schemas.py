from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class TaskBase(BaseModel):
    todo: str
    completed: bool = False
    user_id: int


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    todo: Optional[str] = None
    completed: Optional[bool] = None


class TaskRead(TaskBase):
    id: int
    external_id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    nats_connected: bool

    class Config:
        from_attributes = True
