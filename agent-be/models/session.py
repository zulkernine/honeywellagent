from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Session(BaseModel):
    session_id: str
    user_id: str = "admin"
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SessionCreate(BaseModel):
    title: Optional[str] = None   # if None, set from first user message
