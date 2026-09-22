"""
API schemas (request/response Pydantic models).
Kept separate so FastAPI generates a clean OpenAPI spec for Orval codegen.
"""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


# ── Chat ───────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., description="Natural language question or instruction for the agent.", min_length=1)

    model_config = {"json_schema_extra": {"example": {"message": "Show all certificates expiring in 30 days"}}}


class ToolCallOut(BaseModel):
    tool_name: str = Field(..., description="Name of the tool that was invoked.")
    args: dict[str, Any] = Field(..., description="Arguments passed to the tool.")
    result_summary: str = Field(..., description="First 300 chars of the tool's raw result.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "tool_name": "list_expiring_certificates",
                "args": {"days": 30},
                "result_summary": "[{\"cert_id\": \"ABC123\", ...}]",
            }
        }
    }


class ChatResponse(BaseModel):
    session_id: str = Field(..., description="UUID of the session this message belongs to.")
    answer: str = Field(..., description="Final natural-language answer from the agent (Markdown).")
    tool_calls: list[ToolCallOut] = Field(default=[], description="Ordered list of tool calls made during this turn.")
    execution_time_ms: int = Field(..., description="Total wall-clock time for the agent turn in milliseconds.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "b2aec0af-7edd-4212-9f99-6c7355bd18f2",
                "answer": "Here are all customers...",
                "tool_calls": [
                    {
                        "tool_name": "list_customers",
                        "args": {},
                        "result_summary": "[{\"customer_name\": \"Acme Corp\", ...}]",
                    }
                ],
                "execution_time_ms": 1842,
            }
        }
    }


# ── Sessions ───────────────────────────────────────────────────────────────────

class SessionOut(BaseModel):
    session_id: str = Field(..., description="Unique session UUID.")
    title: str = Field(..., description="Session title — set from the first user message, never updated.")
    user_id: str = Field(..., description="Owner of the session.")
    created_at: datetime = Field(..., description="When the session was created.")
    updated_at: datetime = Field(..., description="When the session was last active.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "b2aec0af-7edd-4212-9f99-6c7355bd18f2",
                "title": "Show all certificates expiring in 30 days",
                "user_id": "admin",
                "created_at": "2026-09-22T06:00:00Z",
                "updated_at": "2026-09-22T06:15:00Z",
            }
        }
    }


class ToolCallRecord(BaseModel):
    tool_name: str
    args: dict[str, Any]
    result_summary: str


class MessageOut(BaseModel):
    session_id: str
    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    tool_calls: list[ToolCallRecord] = Field(default=[])
    execution_time_ms: Optional[int] = Field(None, description="Only set on assistant messages.")
    created_at: str = Field(..., description="ISO 8601 timestamp.")


class SessionWithMessages(BaseModel):
    session: SessionOut
    messages: list[MessageOut]


# ── Certificates ───────────────────────────────────────────────────────────────

class CertificateOut(BaseModel):
    cert_id: str
    subject: str
    issuer: str
    serial_number: str
    customer_name: str
    domain: str
    san: list[str] = []
    issued_at: str
    expires_at: str
    status: str = Field(..., description="active | expired | revoked | pending_renewal")
    is_revoked: bool
    revocation_reason: Optional[str] = None
    revocation_date: Optional[str] = None
    key_algorithm: str
    key_size: int
    signature_algorithm: str
    environment: str = Field(..., description="production | staging | dev")
    tags: list[str] = []
    created_at: str
    updated_at: str


# ── Health ─────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = Field(..., description="'ok' when the service is healthy.")
    model: str = Field(..., description="Active OpenRouter model name.")
