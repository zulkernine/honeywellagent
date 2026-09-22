# AI Certificate Operations Agent — Root README

**An AI-powered operations assistant for enterprise digital certificate management.**  
Ask natural language questions, inspect certificate health, verify revocations, and generate renewal requests with full tool-call traceability.

---

## Project Structure

```
query-agent/
├── agent-be/                 ← FastAPI backend (Python 3.11+, LangGraph ReAct)
│   ├── ARCHITECTURE.md       ← Backend technical architecture & data flow
│   ├── README.md             ← Backend setup, API reference, run guide
│   ├── test_edge_cases.py    ← Automated validation suite for evaluator edge cases
│   └── ...
├── agent-fe/                 ← React frontend (TypeScript + Vite + Tailwind v4)
│   ├── ARCHITECTURE.md       ← Frontend architecture, layer diagram, markdown normalization
│   ├── README.md             ← Frontend setup, UI guidelines, scripts
│   └── ...
├── Question.md               ← Original problem statement
└── README.md                 ← Project overview & quick start (You are here)
```

---

## Quick Start

### Backend
```bash
cd agent-be
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in MONGODB_URI + OPENROUTER_API_KEY
uvicorn main:app --reload --port 8000
curl -X POST http://localhost:8000/api/certificates/seed
```
→ Full guide: **[agent-be/README.md](./agent-be/README.md)**  
→ Technical Architecture: **[agent-be/ARCHITECTURE.md](./agent-be/ARCHITECTURE.md)**

### Frontend
```bash
cd agent-fe
npm install
npm run dev
```
→ Setup guide: **[agent-fe/README.md](./agent-fe/README.md)**  
→ Architecture & component docs: **[agent-fe/ARCHITECTURE.md](./agent-fe/ARCHITECTURE.md)**

---

## Documentation Index

| Document | Location | What's inside |
|----------|----------|--------------|
| **Root Overview** | [README.md](./README.md) | Project structure, quick start, edge cases handled, sync/async strategy, scalability roadmap |
| **Backend Setup** | [agent-be/README.md](./agent-be/README.md) | Env vars, API endpoints, curl examples, tools, quick tests |
| **Backend Architecture** | [agent-be/ARCHITECTURE.md](./agent-be/ARCHITECTURE.md) | End-to-end data flow, LangGraph ReAct loop, in-memory TTL cache, scalability roadmap |
| **Frontend Setup** | [agent-fe/README.md](./agent-fe/README.md) | Frontend dev server, Tailwind v4 configuration, environment setup |
| **Frontend Architecture** | [agent-fe/ARCHITECTURE.md](./agent-fe/ARCHITECTURE.md) | Layer diagram, optimistic chat flow, markdown table normalization, Zustand store |
| **Problem Statement** | [Question.md](./Question.md) | Enterprise certificate operations agent specifications |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Agent Orchestration** | LangGraph `create_react_agent` + OpenRouter LLM (Claude 3.5 Sonnet / GPT-4o) |
| **Backend Framework** | FastAPI (Python 3.11+) + Uvicorn |
| **Database & Driver** | MongoDB Atlas via Motor (`AsyncIOMotorClient`) |
| **Hot Working Memory** | LangGraph `MemorySaver` (in-process checkpointer with 15-min idle TTL cleanup) |
| **Frontend Framework** | React 19 + TypeScript + Vite + Tailwind CSS v4 |
| **API Client** | Orval OpenAPI codegen (Axios + TanStack React Query v5) |
| **Markdown & Tables** | `react-markdown` + `remark-gfm` + responsive table container |

---

## Edge Cases Handled

The system has been hardened against common edge cases and adversarial prompts:

1. **Missing Certificate ID & Hallucination Prevention**:
   - `fetch_certificate`, `verify_revocation`, and `generate_renewal_request` reject empty or whitespace inputs.
   - `SYSTEM_PROMPT` explicitly instructs the agent never to invent dummy IDs or invoke tools with placeholder arguments; the agent politely asks the user for the ID.
2. **Non-existent Certificates**:
   - Clean structured `{"error": "Certificate 'X' not found."}` returned without throwing unhandled exceptions.
   - Agent explains that the certificate does not exist in the database rather than hallucinating fake dates.
3. **Date Window Boundaries & Overflow Protection**:
   - Boundaries strictly defined as `now <= expires_at <= now + days`, excluding expired and revoked certificates.
   - Clamped `safe_days = min(max(0, days), 3650)` to prevent Python `OverflowError` in `timedelta`.
   - Rejects negative days (`days < 0`) with a clean explanation.
4. **Special Characters & Regex Sanitization in Customer Lookup**:
   - Sanitized using `re.escape(customer_name.strip())` to prevent MongoDB regex errors (`BadValue: Regular expression is invalid`) on queries containing `(`, `*`, `[`, etc.
5. **Action Guardrails for Destructive Mutations (Renewals)**:
   - `generate_renewal_request` checks if the certificate exists, whether it is **already revoked** (rejects renewal and explains a new cert must be issued), and whether it **already has a pending renewal request**.
   - Requires explicit tool execution success with a valid `request_id` before the assistant claims renewal succeeded.
6. **Tool Failure Resiliency (No Generic 500s)**:
   - All tool database queries are wrapped in `try...except`, returning structured error payloads to the ReAct loop so the agent can explain failures gracefully rather than triggering an unhandled 500 HTTP response.
7. **Turn-Scoped Tool Traces**:
   - Scoped tool extraction in `POST /api/chat/{session_id}` to the current conversational turn only (from the last `HumanMessage`), preventing past turns' tool calls from accumulating in the current response.
8. **Timezone Normalization (IST & Global)**:
   - Frontend detects naive UTC strings from the backend and normalizes them with `Z`, preventing timezone offsets (e.g. 5 hours ago in UTC+5:30 / IST).
9. **Markdown Table Parsing & Auto-Repair**:
   - Integrated `remark-gfm` and pre-processing table normalization (`normalizeMarkdownTables`) to repair single-line collapsed tables from LLMs and wrap them in horizontally scrollable containers.
10. **Visual Tool Lifecycle Indicators in UI**:
    - `ToolCallTrace.tsx` visually tags every tool call with an explicit **`SUCCESS`** (emerald) or **`ERROR`** (amber) badge and icon.

---

## Sync / Async Strategy

1. **Fully Asynchronous Execution**:
   - All tools are declared as `async def` and natively awaited by LangGraph's `ainvoke()`.
   - The database layer utilizes Motor (`AsyncIOMotorClient`) for non-blocking I/O, ensuring that concurrent client requests do not block the Python asyncio event loop.
2. **Two-Tier State & Memory Architecture**:
   - **Persistent Tier (MongoDB)**: All conversation turns (`messages`) and session metadata (`sessions`) are durably stored in MongoDB Atlas.
   - **In-Memory Hot Tier (`MemorySaver`)**: LangGraph state checkpointer keeps active threads in process memory for instant multi-turn conversational context.
   - **Background Idle Eviction**: An async background task runs every 60 seconds, evicting threads idle for > 15 minutes to prevent RAM memory leaks.
   - **Auto-Warming on Cache Miss**: Cold restarts or evicted sessions are transparently rehydrated from MongoDB before agent invocation.

---

## Known Limitations & Roadmap (Not Done Due to Time Constraints)

1. **Server-Sent Events (SSE) / WebSocket Streaming**:
   - *Current state*: Standard HTTP POST returning one JSON response; frontend renders an optimistic thinking bubble until the full turn finishes.
   - *Future improvement*: Stream token-by-token output using FastAPI `EventSourceResponse` (SSE) and stream live tool lifecycle events (`tool_start`, `tool_end`).
2. **Stateless Server Architecture for Horizontal Scaling**:
   - *Current state*: In-memory `MemorySaver` hot cache requires sticky sessions if multiple server replicas run behind a load balancer.
   - *Future improvement*: Replace `MemorySaver` with a distributed checkpointer (`RedisSaver` or `MongoDBSaver`) to achieve 100% stateless backend replicas across auto-scaled container pods.
3. **Enterprise Authentication & RBAC**:
   - *Current state*: Default single-tenant admin context suitable for local evaluation.
   - *Future improvement*: Implement OAuth2 / JWT bearer tokens and Role-Based Access Control (e.g., read-only auditor vs SecOps admin authorized to trigger renewals).
4. **Asynchronous Worker Queue for Long-Running Operations**:
   - *Current state*: Tool executions run synchronously within the HTTP request.
   - *Future improvement*: Integrate Celery / Temporal / ARQ to offload bulk renewal batches and automated Certificate Authority (ACME/HSM) integrations to background worker pools.
