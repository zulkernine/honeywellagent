import { AlertTriangle, ChevronDown, Wrench } from 'lucide-react'
import { useState } from 'react'
import type { ToolCall } from '../api/types'

interface Props {
  toolCalls: ToolCall[]
}

export default function ToolCallTrace({ toolCalls }: Props) {
  const [open, setOpen] = useState(true)
  if (toolCalls.length === 0) return null

  return (
    <div className="mt-2 overflow-hidden rounded-xl border border-slate-200 bg-white dark:border-white/10 dark:bg-slate-900/60">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex w-full items-center gap-2 px-3 py-2 text-left text-xs font-medium text-slate-500 transition-colors hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
      >
        <Wrench className="size-3.5" />
        <span>
          Tool calls made ({toolCalls.length})
        </span>
        <ChevronDown
          className={`ml-auto size-3.5 transition-transform ${open ? 'rotate-180' : ''}`}
        />
      </button>
      {open && (
        <ol className="divide-y divide-slate-100 border-t border-slate-200 dark:divide-white/5 dark:border-t-white/10">
          {toolCalls.map((tc, i) => (
            <li key={i} className="px-3 py-2 text-xs">
              <div className="flex items-baseline gap-2">
                <span className="text-slate-400 dark:text-slate-500">{i + 1}.</span>
                <code className="font-mono text-indigo-600 dark:text-indigo-300">
                  {tc.tool_name}
                </code>
                <code className="font-mono text-slate-400 dark:text-slate-500">
                  ({JSON.stringify(tc.args)})
                </code>
              </div>
              <p className="mt-1 flex items-start gap-1.5 break-all pl-5 text-slate-500 dark:text-slate-400">
                <AlertTriangle className="mt-0.5 size-3 shrink-0 text-emerald-500/80" />
                <span>{tc.result_summary}</span>
              </p>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}