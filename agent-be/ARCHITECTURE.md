# Backend Technical Architecture — AI Operations Agent (`agent-be`)

FastAPI backend powering the enterprise digital certificate operations agent. Built with Python 3.11+, LangGraph ReAct agent, OpenRouter LLM integration, and MongoDB Atlas.

---

## 1. Stack & Technologies

| Layer | Technology | Purpose |
|---|---|---|
| **API Framework** | FastAPI + Uvicorn | High-performance asynchronous REST API with auto-generated OpenAPI / Swagger specs |
| **Agent Orchestration** | LangGraph (`create_react_agent`) | Stateful ReAct execution graph with tool binding, reasoning loops, and checkpointing |
| **LLM Provider** | OpenRouter (`ChatOpenAI` via OpenRouter endpoint) | Model flexibility (Claude 3.5 Sonnet, GPT-4o, Gemini 1.5 Pro) with unified OpenAI-compatible SDK |
| **Hot Cache / Working Memory**| LangGraph `MemorySaver` | Low-latency in-memory conversation thread state |
| **Persistent Storage** | MongoDB Atlas via Motor (AsyncIOMotorClient) | Durable persistence for certificates, sessions, and complete message / tool trace history |
| **Data Validation** | Pydantic v2 | Strict schema validation, request/response models, and OpenAPI serialization |

---

## 2. Architecture & Layer Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             CLIENT LAYER                                    │
│       React SPA (agent-fe) / REST API Consumer / cURL                       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / JSON
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                             FASTAPI ROUTERS                                 │
│  /api/chat/{session_id}  ·  /api/sessions/*  ·  /api/certificates/*  ·  /health
└───────────────┬─────────────────────────────────────────────────────────────┘
                │
    ┌───────────┴──────────────────────────────┐
    ▼                                          ▼
┌────────────────────────────┐   ┌────────────────────────────────────────────┐
│   MEMORY & SESSION MGR     │   │             DATABASE LAYER                 │
│  - ensure_session_in_memory│   │  database.py (AsyncIOMotorClient)          │
│  - touch_session / TTL     │   │  Collections:                              │
│  - cleanup_idle_sessions   │   │  • `certificates` (inventory & audit logs) │
│  - LangGraph MemorySaver   │   │  • `sessions` (metadata & titles)          │
└───────────────┬────────────┘   │  • `messages` (roles, content, tool traces)│
                │                └─────────────────────▲──────────────────────┘
                ▼                                      │ read / write
┌───────────────────────────────────────────┐          │
│          LANGGRAPH REACT AGENT            │          │
│  System prompt + ChatOpenAI (OpenRouter)  │          │
│  Execution loop (Reason → Act → Observe)  │          │
│  Tools:                                   │          │
│  • fetch_certificate ─────────────────────┼──────────┘
│  • list_expiring_certificates ────────────┤
│  • verify_revocation ─────────────────────┤
│  • generate_renewal_request ──────────────┤
│  • list_certificates_by_customer ─────────┤
│  • list_customers ────────────────────────┘
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. End-to-End Chat Data Flow

When a user submits a query to `POST /api/chat/{session_id}`:

```
1. Client POST /api/chat/{session_id}
   │
   ▼
2. Session Resolution & Metadata
   ├── Look up session_id in MongoDB `sessions`
   └── If not present, create new session (title auto-derived from first 80 chars of user prompt)
   │
   ▼
3. Memory Hydration (Cache Miss / Eviction Check)
   ├── Check if session thread exists in LangGraph in-memory `MemorySaver`
   └── If absent (cache miss or cold server restart):
       Query MongoDB `messages` for session history and replay into `MemorySaver`
   │
   ▼
4. Persist User Message
   └── Insert `Message(role="user", content=...)` into MongoDB `messages`
   │
   ▼
5. LangGraph ReAct Agent Invocation
   ├── Invoke agent: `agent.ainvoke({"messages": [HumanMessage(content)]}, config={"configurable": {"thread_id": session_id}})`
   ├── Reasoning step: LLM analyzes user intent and decides whether tool execution is necessary
   ├── Tool Execution:
   │   - If tool required: LangGraph executes tool (e.g., `list_expiring_certificates(days=30)`)
   │   - Tool queries MongoDB asynchronously and returns structured JSON output
   │   - Output injected back into thread as `ToolMessage`
   └── Synthesis step: LLM consumes tool output and generates markdown answer
   │
   ▼
6. Trace Extraction & Metrics
   ├── Parse message history to extract `AIMessage.tool_calls` and matching `ToolMessage` outputs
   ├── Compute turn wall-clock duration `execution_time_ms`
   └── Format structured `tool_calls` trace (`tool_name`, `args`, `result_summary`)
   │
   ▼
7. Persist Assistant Message
   └── Insert `Message(role="assistant", content=answer, tool_calls=..., execution_time_ms=...)` into MongoDB
   │
   ▼
8. Response to Client
   └── Return `ChatResponse(session_id, answer, tool_calls, execution_time_ms)`
```

---

## 4. State & Memory Management

The backend uses a **two-tier state architecture**:

1. **Persistent Source of Truth (MongoDB)**:
   - All conversation turns (`messages` collection) and session records (`sessions` collection) are durably committed to MongoDB.
   - Any crash or restart retains 100% of conversation history and tool outputs.

2. **In-Memory Working Memory (LangGraph `MemorySaver`)**:
   - `MemorySaver` maintains active graph states in process memory for near-instantaneous multi-turn conversational context.
   - **TTL & Eviction**: Background task `cleanup_idle_sessions` runs every 60 seconds. If a session has not been touched in > 15 minutes, its thread state is pruned from memory to prevent memory leaks.
   - **Transparent Re-warming**: `ensure_session_in_memory` detects cache misses upon subsequent requests and transparently rehydrates thread history from MongoDB before invoking the agent.

---

## 5. Next Improvements & Scalability Roadmap

### 1. Server-Sent Events (SSE) / WebSocket Streaming
- **Current state**: Non-streaming JSON response; frontend displays optimistic "thinking" spinner until the entire ReAct loop finishes.
- **Improvement**:
  - Implement `GET /api/chat/{session_id}/stream` using FastAPI `EventSourceResponse` (SSE) or WebSockets.
  - Stream granular events to the frontend in real-time:
    1. `event: tool_start` (e.g. `{"tool": "list_expiring_certificates", "args": {"days": 30}}`)
    2. `event: tool_end` (execution status and summary)
    3. `event: token` (stream answer tokens incrementally as LLM generates them)
    4. `event: done` (turn summary and total execution time)
  - **Benefits**: Dramatically improves perceived latency (First Contentful Token within ~300ms) and provides transparent visibility into agent actions.

### 2. Stateless Server Architecture for Horizontal Scalability
- **Current state**: In-process `MemorySaver` requires sticky sessions if multiple server replicas run behind a load balancer.
- **Improvement**:
  - Swap `MemorySaver` with a distributed checkpointer such as `RedisSaver` or a custom `MongoDBSaver`.
  - Alternatively, pass the recent window of messages from MongoDB directly into stateless agent invocations.
  - **Benefits**: Eliminates server affinity, enables horizontal scaling across auto-scaled Kubernetes pods / ECS tasks, and guarantees zero loss of in-flight sessions during rolling deployments.

### 3. Asynchronous / Background Worker Execution
- **Current state**: Tool operations run synchronously within the HTTP request lifecycle.
- **Improvement**:
  - Integrate a distributed task queue (Celery, ARQ, or Temporal) for heavy or external write operations (e.g., bulk renewal workflows, ACME protocol issuance, HSM re-keying, DNS challenge verification).
  - Agent can trigger tasks, receive a task ID, and poll or notify the user upon asynchronous job completion.

### 4. Authentication, Authorization & RBAC
- **Current state**: Open endpoints intended for local/demonstration environments.
- **Improvement**:
  - Add OAuth2 / JWT bearer authentication.
  - Implement Role-Based Access Control (RBAC):
    - `Auditor`: Read-only queries (`fetch_certificate`, `list_expiring_certificates`, `verify_revocation`).
    - `SecOps / Cert Admin`: Mutation queries (`generate_renewal_request`, certificate creation/patching).
  - Multi-tenancy: Partition MongoDB queries by `organization_id` or `tenant_id`.

### 5. Vector Search & Hybrid RAG for Certificate Knowledge Base
- **Current state**: Structured MongoDB queries based on explicit filters.
- **Improvement**:
  - Index company security policies, compliance standards (e.g., CAB Forum guidelines, internal TLS policy manuals), and incident runbooks into a vector store (e.g., MongoDB Atlas Vector Search).
  - Hybrid retrieval allows the agent to answer both operational queries ("which cert is expiring?") and policy questions ("what is our policy on RSA 2048 key deprecation?").

### 6. Production Observability & Tracing
- **Current state**: Standard Python logging and execution time measurement.
- **Improvement**:
  - Integrate OpenTelemetry and LLM observability platforms (LangSmith, Langfuse, or Arize Phoenix).
  - Track per-tool latency, token consumption, cost analysis, and detect model hallucinations or tool call failures.
