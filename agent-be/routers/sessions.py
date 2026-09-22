"""
Sessions router – CRUD for chat sessions and message history retrieval.
GET  /api/sessions               – list all sessions (sidebar)
POST /api/sessions               – create a new blank session
GET  /api/sessions/{session_id}  – get session + full message history
DELETE /api/sessions/{session_id} – delete session + its messages
"""
import uuid
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException

from database import get_db
from models.session import Session
from schemas import SessionOut, SessionWithMessages

router = APIRouter(prefix="/api/sessions", tags=["sessions"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[SessionOut])
async def list_sessions():
    """Return all sessions sorted by most recently updated (for sidebar)."""
    db = get_db()
    cursor = db.sessions.find({"user_id": "admin"}).sort("updated_at", -1)
    docs = await cursor.to_list(length=200)
    for d in docs:
        d.pop("_id", None)
    return docs


@router.post("", response_model=SessionOut, status_code=201)
async def create_session():
    """Create a new blank session. Returns session_id for the frontend to use."""
    db = get_db()
    session = Session(
        session_id=str(uuid.uuid4()),
        title="New conversation",
    )
    doc = session.model_dump()
    await db.sessions.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.get("/{session_id}", response_model=SessionWithMessages)
async def get_session(session_id: str):
    """Get a session and its full message history."""
    db = get_db()
    session_doc = await db.sessions.find_one({"session_id": session_id})
    if not session_doc:
        raise HTTPException(status_code=404, detail="Session not found.")
    session_doc.pop("_id", None)

    cursor = db.messages.find({"session_id": session_id}).sort("created_at", 1)
    messages = await cursor.to_list(length=1000)
    for m in messages:
        m.pop("_id", None)
        if "created_at" in m and isinstance(m["created_at"], datetime):
            m["created_at"] = m["created_at"].isoformat()

    return {"session": session_doc, "messages": messages}


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: str):
    """Delete a session and all its messages."""
    db = get_db()
    result = await db.sessions.delete_one({"session_id": session_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found.")
    await db.messages.delete_many({"session_id": session_id})
