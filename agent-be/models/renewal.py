from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class RenewalRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cert_id: str
    status: str = "pending"           # pending | approved | completed | rejected
    reason: str
    requested_by: str = "admin"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
