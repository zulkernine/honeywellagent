import { Send } from 'lucide-react'
import { useCallback, useEffect, useRef } from 'react'
import { useUiStore } from '../store/uiStore'

interface Props {
  sessionId: string
  disabled: boolean
  onSend: (message: string) => void
}

export default function Composer({ sessionId, disabled, onSend }: Props) {
  const draft = useUiStore((s) => s.drafts[sessionId] ?? '')
  const setDraft = useUiStore((s) => s.setDraft)
  const clearDraft = useUiStore((s) => s.clearDraft)
  const ref = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (!disabled) ref.current?.focus()
  }, [sessionId, disabled])

  const resize = useCallback(() => {
    const el = ref.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`
  }, [])

  const send = useCallback(() => {
    const text = draft.trim()
    if (!text || disabled) return
    onSend(text)
    clearDraft(sessionId)
    requestAnimationFrame(() => {
      if (ref.current) ref.current.style.height = 'auto'
    })
  }, [draft, disabled, onSend, clearDraft, sessionId])

  return (
    <div className="flex items-end gap-2 rounded-2xl border border-slate-200 bg-slate-50 p-2 shadow-lg shadow-slate-200/60 focus-within:border-indigo-400 dark:border-white/10 dark:bg-slate-800/80 dark:shadow-slate-950/40 dark:focus-within:border-indigo-500/60">
      <textarea
        ref={ref}
        rows={1}
        value={draft}
        disabled={disabled}
        placeholder="Ask about certificates… e.g. “Show all certificates expiring in the next 30 days”"
        className="max-h-40 flex-1 resize-none bg-transparent px-2 py-1.5 text-sm text-slate-800 outline-none placeholder:text-slate-400 disabled:opacity-60 dark:text-slate-100 dark:placeholder:text-slate-500"
        onChange={(e) => {
          setDraft(sessionId, e.target.value)
          resize()
        }}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            send()
          }
        }}
      />
      <button
        type="button"
        onClick={send}
        disabled={disabled || !draft.trim()}
        className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-indigo-600 text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-40"
        aria-label="Send message"
      >
        <Send className="size-4" />
      </button>
    </div>
  )
}