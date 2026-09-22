import { Zap } from 'lucide-react'

export default function ExecutionTimeBadge({ ms }: { ms: number }) {
  return (
    <div className="mt-2 inline-flex items-center gap-1 rounded-full border border-slate-200 bg-white px-2.5 py-0.5 text-[11px] text-slate-500 dark:border-white/10 dark:bg-slate-900/60 dark:text-slate-400">
      <Zap className="size-3 text-amber-500 dark:text-amber-400" />
      Execution time: {ms.toLocaleString()}ms
    </div>
  )
}