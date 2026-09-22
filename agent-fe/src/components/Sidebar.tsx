import { Loader2, MessageSquarePlus, ShieldCheck, Trash2, X } from 'lucide-react'
import type { Session } from '../api/types'
import { useCreateSession, useDeleteSession, useSessions } from '../hooks/useSessions'
import { useUiStore } from '../store/uiStore'
import ThemeToggle from './ThemeToggle'

function relativeDate(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60_000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

export default function Sidebar() {
  const { data: sessions, isLoading } = useSessions()
  const createSession = useCreateSession()
  const deleteSession = useDeleteSession()
  const { activeSessionId, setActiveSession, sidebarOpen, setSidebarOpen } =
    useUiStore()

  const content = (
    <div className="flex h-full w-72 flex-col border-r border-slate-200 bg-white dark:border-white/10 dark:bg-slate-900">
      <div className="flex items-center gap-2.5 px-4 py-4">
        <div className="flex size-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600">
          <ShieldCheck className="size-5 text-white" />
        </div>
        <div className="min-w-0">
          <h1 className="truncate text-sm font-semibold text-slate-900 dark:text-slate-100">
            AI Operations Agent
          </h1>
          <p className="text-[11px] text-slate-400 dark:text-slate-500">
            Enterprise Certificates
          </p>
        </div>
        <ThemeToggle className="ml-auto lg:hidden" />
        <button
          type="button"
          onClick={() => setSidebarOpen(false)}
          className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 lg:hidden dark:text-slate-400 dark:hover:bg-white/5 dark:hover:text-white"
          aria-label="Close sidebar"
        >
          <X className="size-4" />
        </button>
      </div>

      <div className="px-3 pb-3">
        <button
          type="button"
          onClick={() => {
            setSidebarOpen(false)
            createSession.mutate()
          }}
          disabled={createSession.isPending}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-500 disabled:opacity-60"
        >
          {createSession.isPending ? (
            <Loader2 className="size-4 animate-spin" />
          ) : (
            <MessageSquarePlus className="size-4" />
          )}
          New Chat
        </button>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-2 pb-3">
        {isLoading ? (
          <p className="px-2 py-4 text-xs text-slate-400 dark:text-slate-500">
            Loading sessions…
          </p>
        ) : (sessions?.length ?? 0) === 0 ? (
          <p className="px-2 py-4 text-xs text-slate-400 dark:text-slate-500">
            No conversations yet. Start a new chat.
          </p>
        ) : (
          <ul className="space-y-1">
            {(sessions ?? []).map((s: Session) => (
              <li key={s.session_id}>
                <button
                  type="button"
                  onClick={() => {
                    setActiveSession(s.session_id)
                    setSidebarOpen(false)
                  }}
                  className={`group flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-left transition-colors ${
                    activeSessionId === s.session_id
                      ? 'bg-indigo-50 ring-1 ring-indigo-200 dark:bg-indigo-600/20 dark:ring-indigo-500/40'
                      : 'hover:bg-slate-100 dark:hover:bg-white/5'
                  }`}
                >
                  <div className="min-w-0 flex-1">
                    <p
                      className={`truncate text-sm ${
                        activeSessionId === s.session_id
                          ? 'text-indigo-700 dark:text-white'
                          : 'text-slate-700 dark:text-slate-300'
                      }`}
                    >
                      {s.title}
                    </p>
                    <p className="text-[11px] text-slate-400 dark:text-slate-500">
                      {relativeDate(s.updated_at)}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation()
                      deleteSession.mutate(s.session_id)
                    }}
                    className="rounded-lg p-1.5 text-slate-400 opacity-0 transition-opacity hover:bg-slate-200 hover:text-red-500 group-hover:opacity-100 dark:text-slate-500 dark:hover:bg-white/5 dark:hover:text-red-400"
                    aria-label={`Delete session: ${s.title}`}
                  >
                    <Trash2 className="size-3.5" />
                  </button>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )

  return (
    <>
      {/* Desktop */}
      <aside className="hidden lg:block">{content}</aside>

      {/* Mobile drawer */}
      <div
        className={`fixed inset-0 z-40 lg:hidden ${sidebarOpen ? '' : 'pointer-events-none'}`}
      >
        <div
          onClick={() => setSidebarOpen(false)}
          className={`absolute inset-0 bg-black/50 transition-opacity ${
            sidebarOpen ? 'opacity-100' : 'opacity-0'
          }`}
        />
        <div
          className={`absolute inset-y-0 left-0 transition-transform duration-200 ${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          {content}
        </div>
      </div>
    </>
  )
}