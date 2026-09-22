"""
In-memory session manager:
- Tracks which sessions are loaded into LangGraph MemorySaver
- Replays from MongoDB on cache miss
- Evicts sessions idle > 15 minutes via background asyncio task
"""
import asyncio
import logging
from datetime import datetime, timedelta

from langchain_core.messages import HumanMessage, AIMessage
from database import get_db

logger = logging.getLogger(__name__)

# session_id → last active datetime
_active_sessions: dict[str, datetime] = {}

SESSION_TTL_MINUTES = 15
CLEANUP_INTERVAL_SECONDS = 60


async def ensure_session_in_memory(session_id: str, agent, checkpointer) -> None:
    """
    If a session is not tracked in _active_sessions, fetch its message
    history from MongoDB and replay it into LangGraph MemorySaver so the
    agent has full context for the next turn.
    """
    if session_id in _active_sessions:
        touch_session(session_id)
        return

    logger.info(f"Cache miss for session {session_id}. Replaying from MongoDB...")
    db = get_db()
    cursor = db.messages.find({"session_id": session_id}).sort("created_at", 1)
    docs = await cursor.to_list(length=1000)

    if not docs:
        # Brand-new session — nothing to replay
        touch_session(session_id)
        return

    # Build LangChain message history
    history = []
    for doc in docs:
        if doc["role"] == "user":
            history.append(HumanMessage(content=doc["content"]))
        elif doc["role"] == "assistant":
            history.append(AIMessage(content=doc["content"]))

    # Seed MemorySaver by putting the messages directly into the thread state
    config = {"configurable": {"thread_id": session_id}}
    try:
        checkpointer.put(
            config,
            {"v": 1, "channel_values": {"messages": history}, "channel_versions": {}, "versions_seen": {}},
            {},
            {},
        )
    except Exception as e:
        logger.warning(f"Could not seed MemorySaver for {session_id}: {e}. Will start fresh.")

    touch_session(session_id)
    logger.info(f"Replayed {len(history)} messages into memory for session {session_id}")


def touch_session(session_id: str) -> None:
    """Update last-active timestamp for a session."""
    _active_sessions[session_id] = datetime.utcnow()


def evict_session(session_id: str, checkpointer) -> None:
    """Remove a session from in-memory store."""
    _active_sessions.pop(session_id, None)
    # MemorySaver stores data in .storage dict keyed by (thread_id, ...)
    keys_to_delete = [k for k in checkpointer.storage if k[0] == session_id]
    for k in keys_to_delete:
        del checkpointer.storage[k]
    logger.info(f"Evicted idle session {session_id} from memory")


async def cleanup_idle_sessions(checkpointer) -> None:
    """Background task: runs every 60s, evicts sessions idle > TTL."""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
        cutoff = datetime.utcnow() - timedelta(minutes=SESSION_TTL_MINUTES)
        idle = [sid for sid, ts in list(_active_sessions.items()) if ts < cutoff]
        for sid in idle:
            evict_session(sid, checkpointer)
        if idle:
            logger.info(f"Cleanup: evicted {len(idle)} idle session(s)")
