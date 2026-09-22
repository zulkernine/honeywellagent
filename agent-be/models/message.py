from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ToolCallRecord(BaseModel):
    tool_name: str
    args: dict
    result_summary: str


class Message(BaseModel):
    session_id: str
    role: str                          # user | assistant
    content: str
    tool_calls: list[ToolCallRecord] = []
    execution_time_ms: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
