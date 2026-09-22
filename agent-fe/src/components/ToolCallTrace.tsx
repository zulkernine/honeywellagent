import { AlertCircle, CheckCircle2, ChevronDown, Wrench } from 'lucide-react'
import { useState } from 'react'
import type { ToolCall } from '../api/types'

interface Props {
  toolCalls: ToolCall[]
}

function isToolError(summary: string): boolean {
  if (!summary) return false
  const lower = summary.toLowerCase()
  return (
    lower.includes('"error"') ||
    lower.includes('error:') ||
    lower.includes('failed') ||
    lower.includes('not found')
  )
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
          {toolCalls.map((tc, i) => {
            const hasError = isToolError(tc.result_summary)
            return (
              <li key={i} className="px-3 py-2 text-xs">
                <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
                  <span className="text-slate-400 dark:text-slate-500">{i + 1}.</span>
                  <code className="font-mono font-semibold text-indigo-600 dark:text-indigo-300">
                    {tc.tool_name}
                  </code>
                  <code className="font-mono text-slate-400 dark:text-slate-500">
                    ({JSON.stringify(tc.args)})
                  </code>
                  <span
                    className={`ml-auto inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${
                      hasError
                        ? 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300'
                        : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300'
                    }`}
                  >
                    {hasError ? (
                      <>
                        <AlertCircle className="size-2.5" />
                        <span>ERROR</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="size-2.5" />
                        <span>SUCCESS</span>
                      </>
                    )}
                  </span>
                </div>
                <div className="mt-1 flex items-start gap-1.5 break-all pl-4 text-slate-500 dark:text-slate-400">
                  <span className="font-mono text-[11px] leading-relaxed">
                    {tc.result_summary}
                  </span>
                </div>
              </li>
            )
          })}
        </ol>
      )}
    </div>
  )
}