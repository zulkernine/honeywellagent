# AI Certificate Operations Agent – Backend

FastAPI backend powering the AI Operations Agent for enterprise certificate management.

---

## Prerequisites

- Python 3.11+
- A MongoDB Atlas cluster (or local MongoDB 6+)
- An [OpenRouter](https://openrouter.ai/) API key

---

## Setup

### 1. Create & activate a virtual environment

```bash
cd agent-be
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Fill in `.env`

Open `agent-be/.env` and set your real values:

```env
# MongoDB
MONGODB_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/cert_agent?retryWrites=true&w=majority
MONGODB_DB_NAME=cert_agent

# OpenRouter LLM (pick any model available on openrouter.ai)
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# App
APP_ENV=development
CORS_ORIGINS=http://localhost:5173
```

> **Tip**: Other supported models: `openai/gpt-4o`, `google/gemini-flash-1.5`, `meta-llama/llama-3.1-70b-instruct`

---

## Run the server

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at: **http://localhost:8000**

---

## Seed demo data

After the server is running, seed 30 realistic sample certificates:

```bash
curl -X POST http://localhost:8000/api/certificates/seed
```

You should see: `{"message": "Seeded 30 new certificates (skipped existing)."}`

---

## API Reference

### Health
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check + active model name |

### Chat (Agent)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/chat/{session_id}` | Send a message to the agent for a session |

**Request body:**
```json
{ "message": "Show all certificates expiring in next 30 days" }
```
**Response:**
```json
{
  "session_id": "...",
  "answer": "Here are 8 certificates expiring in the next 30 days...",
  "tool_calls": [
    { "tool_name": "list_expiring_certificates", "args": {"days": 30}, "result_summary": "..." }
  ],
  "execution_time_ms": 1234
}
```

### Sessions
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/sessions` | List all sessions (for sidebar) |
| `POST` | `/api/sessions` | Create a new blank session |
| `GET` | `/api/sessions/{session_id}` | Get session + full message history |
| `DELETE` | `/api/sessions/{session_id}` | Delete session + messages |

### Certificates
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/certificates` | List all certs (filter by `?customer=` or `?status=`) |
| `GET` | `/api/certificates/{cert_id}` | Get a single certificate |
| `POST` | `/api/certificates` | Create a certificate |
| `PATCH` | `/api/certificates/{cert_id}` | Update a certificate |
| `POST` | `/api/certificates/seed` | Seed 30 demo certificates |

---

## Interactive Docs

FastAPI auto-generates Swagger UI at:
- **http://localhost:8000/docs** – Swagger / OpenAPI UI
- **http://localhost:8000/redoc** – ReDoc UI

---

## Example Queries to Test the Agent

Start a new session:
```bash
SESSION=$(curl -s -X POST http://localhost:8000/api/sessions | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
echo "Session: $SESSION"
```

Send a message:
```bash
curl -s -X POST "http://localhost:8000/api/chat/$SESSION" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show all certificates expiring in next 30 days"}' | python3 -m json.tool
```

Other test messages:
```bash
# Check a certificate
curl -s -X POST "http://localhost:8000/api/chat/$SESSION" \
  -H "Content-Type: application/json" \
  -d '{"message": "Check certificate ABC123 status"}'

# Verify revocation
curl -s -X POST "http://localhost:8000/api/chat/$SESSION" \
  -H "Content-Type: application/json" \
  -d '{"message": "Verify if certificate XYZ789 is revoked"}'

# Generate renewal
curl -s -X POST "http://localhost:8000/api/chat/$SESSION" \
  -H "Content-Type: application/json" \
  -d '{"message": "Generate renewal request for certificate ABC123"}'

# List by customer
curl -s -X POST "http://localhost:8000/api/chat/$SESSION" \
  -H "Content-Type: application/json" \
  -d '{"message": "List certificates belonging to Customer A"}'
```

---

## Architecture Notes

### In-Memory Session Cache

The LangGraph `MemorySaver` keeps conversation history in process RAM, keyed by `session_id`.

| Scenario | Behaviour |
|----------|-----------|
| Active session | Context immediately available, `touch_session()` called on each request |
| Cache miss (restart) | Messages replayed from MongoDB `messages` collection into `MemorySaver` |
| Idle > 15 minutes | Session evicted from memory by background cleanup task (runs every 60s) |
| After eviction | Auto re-warmed from DB on next request — transparent to user |

> **Tradeoff**: In-memory state is lost on process restart and is not horizontally scalable. For production, replace `MemorySaver` with a `MongoDBSaver` or Redis-backed checkpointer.

### Agent Tools

| Tool | Purpose |
|------|---------|
| `fetch_certificate` | Get full cert details by ID |
| `list_expiring_certificates` | Find certs expiring within N days |
| `verify_revocation` | Check revocation status |
| `generate_renewal_request` | Create renewal action + update cert status |
| `list_certificates_by_customer` | Filter certs by customer name |
| `list_customers` | Aggregate statistics across all customers |

---

## Technical Architecture & Deep Dive

For the complete technical breakdown, see **[ARCHITECTURE.md](./ARCHITECTURE.md)**.

### Data Flow Summary
1. **Client Request**: `POST /api/chat/{session_id}` received by FastAPI.
2. **Session & Memory Warmup**: Session resolved in MongoDB; in-memory `MemorySaver` warmed from DB history on cache miss.
3. **Persist User Message**: Incoming user prompt stored in MongoDB `messages`.
4. **LangGraph ReAct Execution**: Agent reasons, calls MongoDB tools asynchronously as needed, and synthesizes answers.
5. **Trace & Metrics Extraction**: Captures tool inputs/outputs and execution duration.
6. **Persist & Return**: Assistant response and tool trace saved in DB; structured `ChatResponse` returned.

### Next Improvements & Roadmap
- **Server-Sent Events (SSE) / WebSocket Streaming**: Stream answer tokens and live tool invocation events (`tool_start`, `tool_end`) to replace the polling/blocking request pattern.
- **Stateless Server Architecture**: Migrate from in-memory `MemorySaver` to a distributed checkpointer (`RedisSaver` or `MongoDBSaver`) to enable horizontal multi-replica scalability behind load balancers.
- **Asynchronous Task Queue**: Offload bulk certificate renewals and automated CA interactions to Celery/Temporal workers.
- **Role-Based Access Control (RBAC)**: Enforce granular permissions between auditor roles and SecOps administrators.
- **Hybrid RAG**: Index enterprise security and compliance standards in MongoDB Atlas Vector Search for policy-aware answers.
- **Observability**: Integrate OpenTelemetry and Langfuse/LangSmith for tracing agent reasoning paths and latency breakdown.

