# AI Operations Agent – Enterprise Certificates

## Overview

A full-stack AI Agent application that lets operations teams query and act on enterprise certificate data using natural language. The agent uses a **LangGraph built-in ReAct agent** backed by **OpenRouter LLM**, with **FastAPI** as the backend, **MongoDB** for persistence, and a **React** frontend.

---

## Architecture Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          REACT FRONTEND                              │
│  ┌─────────────────┐   ┌──────────────────────────────────────────┐ │
│  │  Session Sidebar │   │            Chat Panel                    │ │
│  │  ─────────────  │   │  ┌──────────────────────────────────┐    │ │
│  │  [Session 1]    │   │  │  User Question Input + Send Btn  │    │ │
│  │  [Session 2]    │   │  └──────────────────────────────────┘    │ │
│  │  [+ New Chat]   │   │  Answer Window (Markdown / Streaming)    │ │
│  │                 │   │  Tool Calls Trace: [1. ... 2. ...]       │ │
│  │                 │   │  Execution Time: Xms                     │ │
│  └─────────────────┘   └──────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────────┘
                      │  REST / SSE (Streaming)
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND                              │
│                                                                      │
│  POST /api/chat/{session_id}   GET /api/sessions                    │
│  GET  /api/sessions/{id}       POST /api/sessions (new)             │
│  GET  /api/certificates        POST /api/certificates               │
│  GET  /api/certificates/{id}   PATCH /api/certificates/{id}         │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                   LangGraph ReAct Agent                        │ │
│  │   create_react_agent(llm, tools, checkpointer=MemorySaver())  │ │
│  │                                                                │ │
│  │   Tools:                                                       │ │
│  │   ├── fetch_certificate(cert_id)                               │ │
│  │   ├── list_expiring_certificates(days)                         │ │
│  │   ├── verify_revocation(cert_id)                               │ │
│  │   ├── generate_renewal_request(cert_id, reason?)               │ │
│  │   └── list_certificates_by_customer(customer_name)             │ │
│  └──────────────────────┬─────────────────────────────────────────┘ │
│                         │                                            │
│  ┌──────────────────────▼─────────────────────────────────────────┐ │
│  │              OpenRouter LLM (model from .env)                  │ │
│  │   ChatOpenAI(base_url="https://openrouter.ai/api/v1", ...)     │ │
│  └──────────────────────────────────────────────────────────────--┘ │
└─────────────────────────────────────────────────────────────────────┘
                      │  PyMongo / Motor (async)
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          MONGODB                                     │
│   Collections: certificates | sessions | messages | renewal_requests│
└─────────────────────────────────────────────────────────────────────┘
```

---

## Agent Reasoning Loop (Per Request)

```
User Input
    │
    ▼
[ReAct Agent] ──── Analyze Intent ────► Is tool needed?
    │                                        │
    │◄───── Tool Result ──────  YES ────► Execute Tool(s) ──► MongoDB Query
    │
    ▼
Synthesize Answer + Tool Call Trace
    │
    ▼
Persist message to MongoDB (session_id)
    │
    ▼
Stream response to Frontend
```

---

## MongoDB Schema

### Collection: `certificates`

```json
{
  "_id": "ObjectId",
  "cert_id": "ABC123",               // human-readable unique ID
  "subject": "CN=api.example.com",
  "issuer": "DigiCert Global CA",
  "serial_number": "3A:B1:...",
  "customer_name": "Customer A",
  "domain": "api.example.com",
  "san": ["api.example.com", "www.example.com"],
  "issued_at": "ISODate",
  "expires_at": "ISODate",
  "status": "active",               // active | expired | revoked | pending_renewal
  "is_revoked": false,
  "revocation_reason": null,        // keyCompromise | cACompromise | unspecified | null
  "revocation_date": null,
  "key_algorithm": "RSA",
  "key_size": 2048,
  "signature_algorithm": "SHA256withRSA",
  "environment": "production",      // production | staging | dev
  "tags": ["api", "tls"],
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```
**Indexes**: `cert_id` (unique), `customer_name`, `expires_at`, `status`

---

### Collection: `sessions`

```json
{
  "_id": "ObjectId",
  "session_id": "uuid-v4",
  "user_id": "admin",               // hardcoded for now
  "title": "Show expiring certs...", // set once from 1st user message, never updated
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

---

### Collection: `messages`

```json
{
  "_id": "ObjectId",
  "session_id": "uuid-v4",
  "role": "user",                   // user | assistant
  "content": "Show all certs expiring in 30 days",
  "tool_calls": [                   // populated for assistant messages
    {
      "tool_name": "list_expiring_certificates",
      "args": { "days": 30 },
      "result_summary": "Found 12 certificates"
    }
  ],
  "execution_time_ms": 342,         // populated for assistant messages
  "created_at": "ISODate"
}
```

---

### Collection: `renewal_requests`

```json
{
  "_id": "ObjectId",
  "request_id": "uuid-v4",
  "cert_id": "ABC123",
  "status": "pending",              // pending | approved | completed | rejected
  "reason": "Expiring in 15 days",
  "requested_by": "admin",
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

---

## Environment File (`.env`)

```env
# MongoDB
MONGODB_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/cert_agent?retryWrites=true&w=majority
MONGODB_DB_NAME=cert_agent

# OpenRouter LLM
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet   # or openai/gpt-4o, google/gemini-flash-1.5

# App
APP_ENV=development
CORS_ORIGINS=http://localhost:5173
```

---

## Project Structure

```
query-agent/
├── backend/
│   ├── .env                        # ← you fill this
│   ├── requirements.txt
│   ├── main.py                     # FastAPI app entrypoint
│   ├── config.py                   # Load .env, settings
│   ├── database.py                 # Motor async MongoDB client
│   ├── models/
│   │   ├── certificate.py          # Pydantic models
│   │   ├── session.py
│   │   ├── message.py
│   │   └── renewal.py
│   ├── routers/
│   │   ├── chat.py                 # POST /api/chat/{session_id}
│   │   ├── sessions.py             # GET/POST /api/sessions
│   │   └── certificates.py        # CRUD for certificates (also seed data)
│   ├── agent/
│   │   ├── agent.py                # create_react_agent setup
│   │   ├── tools.py                # All 5 @tool definitions
│   │   └── llm.py                  # OpenRouter ChatOpenAI config
│   └── seed_data.py                # Script to seed sample certs
│
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx
    │   ├── api/                    # Axios API calls
    │   │   ├── chat.ts
    │   │   └── sessions.ts
    │   ├── components/
    │   │   ├── Sidebar.tsx          # Session list + New Chat
    │   │   ├── ChatPanel.tsx        # Answer + Tool trace + Execution time
    │   │   ├── MessageBubble.tsx    # User/Assistant message renderer
    │   │   └── ToolCallTrace.tsx    # Expandable tool call list
    │   ├── hooks/
    │   │   └── useChat.ts
    │   └── styles/
    │       └── index.css
```

---

## Backend – Key Implementation Notes

### LangGraph Agent
```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_react_agent(
    model=llm,          # OpenRouter ChatOpenAI
    tools=tools,        # list of @tool functions
    checkpointer=MemorySaver()  # in-memory per thread (session)
)
# Invoke with thread_id = session_id for chat history
config = {"configurable": {"thread_id": session_id}}
result = agent.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
```

### Tools (5 total)
| Tool | DB Operation |
|------|-------------|
| `fetch_certificate(cert_id)` | Find by `cert_id` |
| `list_expiring_certificates(days)` | Find where `expires_at <= now+days` and not revoked |
| `verify_revocation(cert_id)` | Return `is_revoked`, `revocation_reason`, `revocation_date` |
| `generate_renewal_request(cert_id, reason?)` | Insert into `renewal_requests`, update cert status |
| `list_certificates_by_customer(customer_name)` | Find by `customer_name` |

### In-Memory Chat Session Persistence

LangGraph's `MemorySaver` stores the full message thread **in the server process RAM**, keyed by `thread_id` (= `session_id`).

```python
# Single global instance — shared across all requests in the process
memory = MemorySaver()
agent = create_react_agent(model=llm, tools=tools, checkpointer=memory)

# Each session gets its own isolated thread in that same in-memory store
config = {"configurable": {"thread_id": session_id}}
```

**What this means:**
- ✅ Agent automatically has full conversational context for follow-up questions within a session.
- ✅ Zero extra DB reads per turn — memory is instantly available.
- ⚠️ State is **lost on server restart** — session context needs to be replayed from MongoDB `messages` collection if the process restarts (tradeoff to document in `README.md`).
- ⚠️ Not horizontally scalable (multiple workers = split memory) — acceptable for hackathon single-process Uvicorn run.

> Tradeoff note, replay strategy, and production alternative (Redis checkpointer / MongoDB checkpointer) will be documented in `README.md`.

**Session Warm-up (Cache Miss Recovery)**

If a `session_id` arrives but is **not in `MemorySaver`** (e.g. after a restart, or first request on a new process):
1. Fetch all `messages` for that `session_id` from MongoDB, ordered by `created_at`.
2. Replay them into the agent's `MemorySaver` by invoking a no-op pass with the full history reconstructed as `HumanMessage` / `AIMessage` pairs.
3. Continue normally — subsequent turns have full context.

```python
# Pseudocode – agent/memory_manager.py
async def ensure_session_in_memory(session_id: str):
    if session_id not in active_sessions:
        messages = await db.messages.find({"session_id": session_id}).sort("created_at", 1)
        # Replay history into MemorySaver thread
        replay_history(agent, session_id, messages)
        touch_session(session_id)   # set last_active = now
```

**15-Minute Inactivity Cleanup**

A lightweight background task (FastAPI `lifespan` + `asyncio`) evicts idle sessions:

```python
# Pseudocode – agent/memory_manager.py
active_sessions: dict[str, datetime] = {}   # session_id → last_active timestamp

def touch_session(session_id: str):
    active_sessions[session_id] = datetime.utcnow()

async def cleanup_idle_sessions(interval_sec=60, ttl_min=15):
    """Runs every 60s, evicts sessions idle > 15 min."""
    while True:
        await asyncio.sleep(interval_sec)
        cutoff = datetime.utcnow() - timedelta(minutes=ttl_min)
        to_evict = [sid for sid, ts in active_sessions.items() if ts < cutoff]
        for sid in to_evict:
            memory.storage.pop(sid, None)   # remove from MemorySaver internals
            active_sessions.pop(sid, None)
```

Started in `lifespan`:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(cleanup_idle_sessions())
    yield
```

- `touch_session()` called on **every** incoming request for that session.
- Evicted sessions are silently re-warmed from MongoDB on next request — transparent to the user.

---

### Chat Endpoint Flow
1. Receive `user_input` + `session_id`
2. If new session → create session doc, title = first 60 chars of user_input
3. Save user `message` doc
4. Run agent with `thread_id=session_id`
5. Collect tool calls + execution time from result
6. Save assistant `message` doc with tool call trace
7. Return response (streaming via SSE optional)

---

## Frontend – Key UI Components

| Component | Responsibility |
|-----------|---------------|
| `Sidebar` | List all sessions (title + date), "New Chat" button |
| `ChatPanel` | Full conversation thread for active session |
| `MessageBubble` | Renders user / assistant messages with markdown |
| `ToolCallTrace` | Collapsible list: `1. tool_name(args) → result` |
| Execution badge | Shows response time in ms at bottom of each assistant turn |

---

## Build Order

1. **[ ] `.env` file** – create with placeholders
2. **[ ] MongoDB seed data** – 30+ realistic sample certificates
3. **[ ] Backend models + DB client** – Pydantic schemas, Motor setup
4. **[ ] Agent tools** – 5 tool functions wired to MongoDB
5. **[ ] LangGraph ReAct agent** – OpenRouter LLM + tools + MemorySaver
6. **[ ] FastAPI routers** – chat, sessions, certificates endpoints
7. **[ ] React frontend** – Sidebar + Chat panel with tool trace
8. **[ ] End-to-end smoke test** – run all 5 example queries
9. **[ ] (Later) User auth** – add per-user scoping

---

## Open Questions

> [!IMPORTANT]
> Please share the **MongoDB URI** whenever ready so it can be added to `.env`.

> [!NOTE]
> **Streaming preference**: Should the agent stream tokens to the UI in real time (SSE), or is a single JSON response sufficient for the hackathon demo?

> [!NOTE]
> **Seed data**: Should I generate realistic certificate data with varied expiry windows, customers, and revocation states for demo purposes?
