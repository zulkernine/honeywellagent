# AI Operations Agent – Frontend (`agent-fe`)

React + Vite + TypeScript chat UI for the certificate operations agent. One page: session sidebar on the left, chat panel in the center with markdown answers, tool-call traces, and execution-time badges.

Stack: **Tailwind CSS v4** (light/dark theme), **TanStack Query** (server state, optimistic chat updates), **Zustand** (UI state), **react-markdown**, and an **Orval-generated** axios + react-query client.

> 📐 For the full architecture, data-flow diagrams (layer diagram, chat optimistic-update flow, scroll management), markdown-table normalization, and the state-ownership matrix, see **[ARCHITECTURE.md](./ARCHITECTURE.md)**.

## Running

The frontend expects the backend (`agent-be/`) running on port 8000:

```bash
cd ../agent-be
uvicorn main:app --reload --port 8000
```

Then:

```bash
npm install
npm run dev
```

Open http://localhost:5173. All `/api/*` requests are proxied to `http://localhost:8000` by the Vite dev server (`vite.config.ts`), so no CORS setup is needed in dev (the backend also allows `http://localhost:5173` via `CORS_ORIGINS`).

### Production build

```bash
npm run build   # typecheck (tsc) + vite build → dist/
npm run preview
```

## API client (Orval codegen)

The API layer is **generated from the backend OpenAPI schema** — there is no hand-written or mock data.

```bash
npm run generate   # backend must be running; reads http://localhost:8000/openapi.json
```

- Config: `orval.config.ts` → outputs into `src/api/generated/` (react-query client, axios).
- HTTP layer: `src/api/mutator.ts` (axios instance; relative `/api` URLs go through the Vite dev proxy).
- `src/api/client.ts` re-exports the generated functions under stable names (`listSessions`, `createSession`, `getSession`, `deleteSession`, `postChat`).
- `src/hooks/` wrap them with TanStack Query keys, invalidation, and optimistic chat updates — components never call the API directly.

Regenerate after any backend API change (`npm run generate`), then run `npm run build` to catch type drift.

## Notes

- The backend chat endpoint is **non-streaming** (single JSON response): sending a message optimistically appends your bubble plus a "thinking" placeholder, which is replaced by the answer, tool-call trace, and execution time when the response arrives.
- In-memory agent state lives server-side (`MemorySaver`); the frontend loads history via `GET /api/sessions/{id}` when switching sessions.
- Auto-scroll only follows new answers when you're already near the bottom; otherwise a "jump to latest" button appears.
- Answers pass through a collapsed-table normalizer (`src/utils/markdown.ts`) before rendering, so LLM tables that arrived on one line still render as tables — details in ARCHITECTURE.md §4.
- Enter sends, Shift+Enter adds a newline. Drafts are kept per session while navigating.
- Theme switcher (light/dark) in the sidebar header; preference persists in `localStorage`.