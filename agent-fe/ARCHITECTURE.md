# Frontend Technical Doc — AI Operations Agent (`agent-fe`)

A single-page chat UI for querying and acting on enterprise certificate data. This doc describes the architecture, data flow, and the non-obvious behaviors (optimistic chat, scroll management, markdown table normalization, theming).

---

## 1. Stack

| Concern | Choice | Why |
|---|---|---|
| Build | Vite 8 + React 19 + TypeScript (strict) | Fast dev loop, typed components |
| Styling | Tailwind CSS v4 (`@tailwindcss/vite`) | Utility-first, class-based dark mode via `@custom-variant` |
| Server state | TanStack Query v5 | Caching, invalidation, optimistic updates |
| Client/UI state | Zustand | Active session, mobile drawer, per-session drafts, theme |
| Markdown | react-markdown | LLM answers render as rich markdown (tables, code, lists) |
| API layer | **Orval** codegen (axios + react-query) | Client generated from the backend OpenAPI schema — zero hand-written API code |

---

## 2. Layer Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                        │
│   App.tsx                                                          │
│   ├── Sidebar        (sessions, new chat, delete, ThemeToggle)     │
│   └── ChatPanel                                                    │
│       ├── MessageBubble ── ToolCallTrace / ExecutionTimeBadge      │
│       └── Composer   (Enter=send · Shift+Enter=newline)            │
└──────────────────────────────┬─────────────────────────────────────┘
                               │ props / events only
┌──────────────────────────────▼─────────────────────────────────────┐
│                          HOOKS LAYER                               │
│   useSessions        → GET /api/sessions + create/delete mutations │
│   useSessionMessages → GET /api/sessions/{id} (history load)       │
│   useChat            → POST /api/chat/{id} + OPTIMISTIC update     │
│   (query keys, cache invalidation, optimistic logic live here)     │
└──────────────────────────────┬─────────────────────────────────────┘
┌──────────────────────────────▼─────────────────────────────────────┐
│                          API LAYER (generated)                     │
│   src/api/client.ts      stable names → re-export of generated fns │
│   src/api/generated/*    Orval output from openapi.json (types +   │
│                          axios react-query client)                 │
│   src/api/mutator.ts     custom axios instance, relative /api URLs │
└──────────────────────────────┬─────────────────────────────────────┘
                               │  /api/*  (same origin)
┌──────────────────────────────▼─────────────────────────────────────┐
│   Vite dev proxy  ──────────────►  FastAPI backend (:8000)         │
│   vite.config.ts                    agent-be (LangGraph ReAct)     │
└────────────────────────────────────────────────────────────────────┘

CROSS-CUTTING
├── store/uiStore.ts      Zustand: activeSessionId · sidebarOpen · theme · drafts
├── utils/markdown.ts     normalizeMarkdownTables (collapsed-table repair)
└── components/ThemeToggle  light/dark, persisted in localStorage
```

Components never import the API directly — everything flows through the hooks. That keeps the Orval swap isolated to one layer.

---

## 3. Chat Message Flow (non-streaming backend)

The backend `POST /api/chat/{session_id}` returns **one JSON response** (no SSE), so the UI bridges the gap with optimistic updates:

```
User hits Send
     │
     ▼
onMutate ──► append [user bubble + "thinking" placeholder] to cache
             (cancel in-flight queries, snapshot previous for rollback)
     │
     ▼
POST /api/chat/{session_id} ──► backend: persist user msg → agent → persist answer
     │
     ├─ onError ──► restore snapshot + refetch (server has the user msg)
     │
     └─ onSuccess ──► swap placeholder for real message:
                       { answer(markdown), tool_calls[], execution_time_ms }
                       └─► invalidate sessions list (title set after 1st chat)
```

- Composer is disabled while pending; failed turns show an inline error with a Dismiss action.
- History on session switch comes from `GET /api/sessions/{id}` — the server is the source of truth; the frontend only decorates cached messages with local ids.

---

## 4. Markdown Table Normalization (`utils/markdown.ts`)

LLM output occasionally collapses a markdown table onto one line, e.g.:

```
| Customer | Total | |---|---| | Acme Corp | 9 | | FinTech | 6 |
```

CommonMark then renders it as a plain paragraph. `normalizeMarkdownTables()` repairs this before `react-markdown` sees it:

| Case | Input (collapsed) | Output (fixed) |
|---|---|---|
| Header → rule junction | `... Revoked \| \|---\|---\|` | `... Revoked \|` ⏎ `\|---\|---\|` |
| Row junctions | `\| 0 \| \| FinTech Corp \|` / `\|---\| \| Acme Corp \|` | newline between rows |

Gating rules (so well-formed tables pass through byte-identical):
- Only runs if the text contains both `|` and a `---` rule row.
- Junction regexes match **spaces/tabs only**, never `\n` — real multi-line tables are untouched (verified in tests).

---

## 5. Scroll Management

```
                 ┌── messages container (flex-1, overflow-y-auto) ──┐
 onScroll ──►    │  distance-from-bottom < 120px  ⇒  isNearBottom   │
                 └──────────────────────────────────────────────────┘
                              │                    │
                     isNearBottom=true       isNearBottom=false
                              │                    │
              auto-scroll to new        floating "jump to latest"
              messages (smooth)         button + no auto-scroll
```

- Session switch → instant jump (`behavior: "auto"`) to the bottom.
- New message → smooth scroll **only** if the user was near the bottom (reading history is never interrupted).
- Layout keeps scrolling inside the messages area only: `h-screen` shell, fixed composer, `min-h-0` on the scroll container.

---

## 6. State Ownership

| State | Where | Why |
|---|---|---|
| Sessions list, messages cache | TanStack Query | Server-owned, needs invalidation/rollback |
| Active session, sidebar, drafts, theme | Zustand | Ephemeral UI state, no server sync |
| Optimistic/pending messages | Query cache (`pending` flag on `ChatMessage`) | Rolled back / replaced atomically by the mutation lifecycle |

---

## 7. Theming

- Light is the default; `ThemeToggle` flips a `dark` class on `<html>` (Tailwind v4 `@custom-variant dark (&:where(.dark, .dark *))`).
- Preference persists in `localStorage`; an inline script in `index.html` applies it before first paint (no flash).
- Markdown elements have explicit light/dark rules in `index.css` (tables, code blocks, blockquotes).

---

## 8. Backend Contract → Generated Client

| Frontend call | Generated function | Backend endpoint |
|---|---|---|
| `listSessions` | `listSessionsApiSessionsGet` | `GET /api/sessions` |
| `createSession` | `createSessionApiSessionsPost` | `POST /api/sessions` |
| `getSession` | `getSessionApiSessionsSessionIdGet` | `GET /api/sessions/{id}` |
| `deleteSession` | `deleteSessionApiSessionsSessionIdDelete` | `DELETE /api/sessions/{id}` |
| `postChat` | `chatApiChatSessionIdPost` | `POST /api/chat/{id}` |

`src/api/client.ts` re-exports the generated functions under stable names, so regenerating (`npm run generate`) never touches hooks or components. The messages array on `GET /api/sessions/{id}` is loosely typed in the backend (`list[dict]`) — `useSessionMessages` maps it to the typed `ChatMessage[]` with client-side ids.

---

## 9. File Map

```
src/
├── main.tsx                 QueryClientProvider
├── App.tsx                  layout shell, mobile top bar, welcome screen
├── api/
│   ├── client.ts            stable re-exports of generated functions
│   ├── mutator.ts           axios instance used by generated code
│   ├── generated/           ← Orval output (do not edit by hand)
│   └── types.ts             ChatMessage / ToolCall / Message view types
├── hooks/                   server-state wrappers (see §2)
├── store/uiStore.ts         Zustand UI state
├── utils/markdown.ts        collapsed-table normalization
└── components/              Sidebar · ChatPanel · MessageBubble ·
                             ToolCallTrace · ExecutionTimeBadge ·
                             Composer · ThemeToggle
```