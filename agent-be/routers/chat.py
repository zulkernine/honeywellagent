"""
Chat router – POST /api/chat/{session_id}
Handles user message → agent invocation → persist → return response.
"""
import time
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

from database import get_db
from models.message import Message, ToolCallRecord
from models.session import Session
from agent.agent import agent, checkpointer
from agent.memory_manager import ensure_session_in_memory, touch_session
from schemas import ChatRequest, ChatResponse, ToolCallOut

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)

@router.post("/{session_id}", response_model=ChatResponse)
async def chat(session_id: str, body: ChatRequest):
    db = get_db()
    user_input = body.message.strip()

    if not user_input:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # ── 1. Ensure session exists in DB ───────────────────────────────────────
    existing = await db.sessions.find_one({"session_id": session_id})
    if not existing:
        title = user_input[:80]
        session = Session(session_id=session_id, title=title)
        await db.sessions.insert_one(session.model_dump())

    # ── 2. Warm up in-memory context if needed (cache miss) ──────────────────
    await ensure_session_in_memory(session_id, agent, checkpointer)

    # ── 3. Persist user message ───────────────────────────────────────────────
    user_msg = Message(session_id=session_id, role="user", content=user_input)
    await db.messages.insert_one(user_msg.model_dump())

    # ── 4. Run agent ──────────────────────────────────────────────────────────
    config = {"configurable": {"thread_id": session_id}}
    start_ms = time.time()
    try:
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
        )
    except Exception as e:
        logger.error(f"Agent error for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
    elapsed_ms = int((time.time() - start_ms) * 1000)

    # ── 5. Extract answer + tool call trace ───────────────────────────────────
    messages = result.get("messages", [])
    answer = ""
    tool_calls_out: list[ToolCallOut] = []
    tool_call_id_map: dict[str, dict] = {}  # id → {name, args}

    for msg in messages:
        # Capture tool invocation metadata from AI messages with tool_calls
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_call_id_map[tc["id"]] = {"name": tc["name"], "args": tc["args"]}
        # Capture tool results
        elif isinstance(msg, ToolMessage):
            meta = tool_call_id_map.get(msg.tool_call_id, {})
            result_preview = str(msg.content)[:300]
            tool_calls_out.append(
                ToolCallOut(
                    tool_name=meta.get("name", "unknown"),
                    args=meta.get("args", {}),
                    result_summary=result_preview,
                )
            )

    # Final AI text response is the last AIMessage without tool_calls
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and not msg.tool_calls:
            answer = msg.content
            break

    # ── 6. Persist assistant message ──────────────────────────────────────────
    tool_records = [
        ToolCallRecord(
            tool_name=tc.tool_name,
            args=tc.args,
            result_summary=tc.result_summary,
        )
        for tc in tool_calls_out
    ]
    assistant_msg = Message(
        session_id=session_id,
        role="assistant",
        content=answer,
        tool_calls=tool_records,
        execution_time_ms=elapsed_ms,
    )
    await db.messages.insert_one(assistant_msg.model_dump())

    # Update session updated_at
    await db.sessions.update_one(
        {"session_id": session_id},
        {"$set": {"updated_at": datetime.utcnow()}},
    )

    touch_session(session_id)

    return ChatResponse(
        session_id=session_id,
        answer=answer,
        tool_calls=tool_calls_out,
        execution_time_ms=elapsed_ms,
    )
