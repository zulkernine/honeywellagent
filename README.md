# AI Certificate Operations Agent — Root README

**An AI-powered operations assistant for enterprise digital certificate management.**  
Ask natural language questions, get instant answers with full tool-call traceability.

---

## Project Structure

```
query-agent/
├── agent-be/                 ← FastAPI backend (Python 3.11+, LangGraph ReAct)
│   ├── ARCHITECTURE.md       ← Backend technical architecture & data flow
│   ├── README.md             ← Backend setup, API reference, run guide
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
| **Root Overview** | [README.md](./README.md) | Project structure, quick start, tech stack, documentation index |
| **Backend Setup** | [agent-be/README.md](./agent-be/README.md) | Env vars, API endpoints, curl examples, tools, quick tests |
| **Backend Architecture** | [agent-be/ARCHITECTURE.md](./agent-be/ARCHITECTURE.md) | End-to-end data flow, LangGraph ReAct loop, in-memory TTL cache, scalability roadmap (SSE, stateless checkpointer) |
| **Frontend Setup** | [agent-fe/README.md](./agent-fe/README.md) | Frontend dev server, Tailwind v4 configuration, environment setup |
| **Frontend Architecture** | [agent-fe/ARCHITECTURE.md](./agent-fe/ARCHITECTURE.md) | Layer diagram, optimistic chat flow, markdown table normalization, Zustand store |
| **Problem Statement** | [Question.md](./Question.md) | Enterprise certificate operations agent specifications |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent | LangGraph `create_react_agent` + OpenRouter LLM |
| Backend | FastAPI + Motor (async MongoDB) |
| Session Memory | LangGraph `MemorySaver` (in-process, 15-min TTL) |
| Database | MongoDB Atlas |
| Frontend | React + Vite + TypeScript + Orval (API codegen) |
