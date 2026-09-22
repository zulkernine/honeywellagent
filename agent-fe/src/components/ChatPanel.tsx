import { ArrowDown, RefreshCcw, ShieldCheck } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import type { ChatMessage } from '../api/types'
import { useChat } from '../hooks/useChat'
import { useSessionMessages } from '../hooks/useSessionMessages'
import Composer from './Composer'
import MessageBubble from './MessageBubble'

const EXAMPLE_QUERIES = [
  'Show all certificates expiring in the next 30 days',
  'Check certificate ABC123 status',
  'Verify if certificate XYZ789 is revoked',
  'Generate renewal request for certificate ABC123',
  'List certificates belonging to Customer A',
]

const BOTTOM_THRESHOLD = 120

export default function ChatPanel({ sessionId }: { sessionId: string }) {
  const { data, isLoading } = useSessionMessages(sessionId)
  const chat = useChat(sessionId)
  const messages: ChatMessage[] = data?.messages ?? []

  const scrollRef = useRef<HTMLDivElement>(null)
  const [isNearBottom, setIsNearBottom] = useState(true)
  const sessionKeyRef = useRef(sessionId)

  const scrollToBottom = useCallback((smooth = true) => {
    const el = scrollRef.current
    if (!el) return
    el.scrollTo({
      top: el.scrollHeight,
      behavior: smooth ? 'smooth' : 'auto',
    })
  }, [])

  const handleScroll = useCallback(() => {
    const el = scrollRef.current
    if (!el) return
    const near =
      el.scrollHeight - el.scrollTop - el.clientHeight < BOTTOM_THRESHOLD
    setIsNearBottom(near)
  }, [])

  // Instant jump on session switch; reset near-bottom state.
  useEffect(() => {
    if (sessionKeyRef.current !== sessionId) {
      sessionKeyRef.current = sessionId
      setIsNearBottom(true)
      requestAnimationFrame(() => scrollToBottom(false))
    }
  }, [sessionId, scrollToBottom])

  // Auto-scroll on new messages only when the user is already at the bottom.
  const count = messages.length
  const lastId = messages[count - 1]?.id
  useEffect(() => {
    if (!isNearBottom) return
    const el = scrollRef.current
    if (!el) return
    const hasOverflowed = el.scrollHeight > el.clientHeight
    if (hasOverflowed && count > 0) scrollToBottom(true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [count, lastId])

  const busy = chat.isPending || isLoading

  return (
    <div className="relative flex h-full min-w-0 flex-1 flex-col bg-white dark:bg-slate-950">
      {/* Messages */}
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="min-h-0 flex-1 overflow-y-auto"
      >
        <div className="mx-auto max-w-3xl space-y-5 px-4 py-6">
          {isLoading ? (
            <div className="flex h-64 items-center justify-center text-sm text-slate-400 dark:text-slate-500">
              Loading conversation…
            </div>
          ) : messages.length === 0 ? (
            <EmptyState
              onPick={(q) => {
                if (!chat.isPending) chat.mutate(q)
              }}
            />
          ) : (
            messages.map((m) => <MessageBubble key={m.id} message={m} />)
          )}

          {chat.isError && (
            <div className="flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-300">
              <span className="flex-1">
                Something went wrong: {(chat.error as Error)?.message ?? 'request failed'}
              </span>
              <button
                type="button"
                onClick={() => chat.reset()}
                className="rounded-lg border border-red-300 px-2 py-1 text-xs hover:bg-red-100 dark:border-red-400/40 dark:hover:bg-red-500/20"
              >
                Dismiss
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Jump to latest */}
      {!isNearBottom && !busy && (
        <button
          type="button"
          onClick={() => scrollToBottom(true)}
          className="absolute bottom-28 left-1/2 z-10 flex size-9 -translate-x-1/2 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-500 shadow-lg transition-colors hover:text-slate-800 dark:border-white/10 dark:bg-slate-800 dark:text-slate-300 dark:hover:text-white"
          aria-label="Jump to latest"
        >
          <ArrowDown className="size-4" />
        </button>
      )}

      {/* Composer */}
      <div className="shrink-0 px-4 pb-4">
        <div className="mx-auto max-w-3xl">
          <Composer
            sessionId={sessionId}
            disabled={chat.isPending}
            onSend={(msg) => chat.mutate(msg)}
          />
          <p className="mt-2 text-center text-[11px] text-slate-400 dark:text-slate-600">
            The agent can inspect certificates, verify revocation, and raise
            renewal requests.
          </p>
        </div>
      </div>
    </div>
  )
}

function EmptyState({ onPick }: { onPick: (q: string) => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="flex size-14 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 shadow-lg shadow-indigo-200 dark:shadow-indigo-950/50">
        <ShieldCheck className="size-7 text-white" />
      </div>
      <h2 className="mt-4 text-lg font-semibold text-slate-900 dark:text-slate-100">
        AI Operations Agent
      </h2>
      <p className="mt-1 max-w-sm text-sm text-slate-500 dark:text-slate-400">
        Ask anything about your enterprise certificates — expiry windows,
        revocation status, renewals, and ownership.
      </p>
      <div className="mt-6 flex max-w-md flex-wrap justify-center gap-2">
        {EXAMPLE_QUERIES.map((q) => (
          <button
            key={q}
            type="button"
            onClick={() => onPick(q)}
            className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-slate-600 transition-colors hover:border-indigo-400 hover:text-indigo-600 dark:border-white/10 dark:bg-slate-800/60 dark:text-slate-300 dark:hover:border-indigo-500/50 dark:hover:text-white"
          >
            {q}
          </button>
        ))}
      </div>
      <p className="mt-6 hidden items-center gap-1 text-xs text-slate-400 sm:flex dark:text-slate-600">
        <RefreshCcw className="size-3" /> Enter to send · Shift+Enter for a new line
      </p>
    </div>
  )
}