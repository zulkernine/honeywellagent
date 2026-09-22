import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { ChatMessage } from '../api/types'
import { normalizeMarkdownTables } from '../utils/markdown'
import ExecutionTimeBadge from './ExecutionTimeBadge'
import ToolCallTrace from './ToolCallTrace'

export default function MessageBubble({ message }: { message: ChatMessage }) {
  if (message.pending) {
    return (
      <div className="flex gap-3">
        <Avatar role="assistant" />
        <div className="flex items-center gap-1.5 rounded-2xl rounded-tl-sm border border-slate-200 bg-slate-50 px-4 py-3.5 dark:border-white/10 dark:bg-slate-800/60">
          <Dot delay="0ms" />
          <Dot delay="150ms" />
          <Dot delay="300ms" />
        </div>
      </div>
    )
  }

  if (message.role === 'user') {
    return (
      <div className="flex justify-end gap-3">
        <div className="max-w-[85%] rounded-2xl rounded-tr-sm bg-indigo-600 px-4 py-2.5 text-sm whitespace-pre-wrap text-white shadow-lg shadow-indigo-200/60 dark:shadow-indigo-950/40">
          {message.content}
        </div>
        <Avatar role="user" />
      </div>
    )
  }

  return (
    <div className="flex gap-3">
      <Avatar role="assistant" />
      <div className="max-w-[85%] min-w-0 rounded-2xl rounded-tl-sm border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 shadow-md shadow-slate-200/70 dark:border-white/10 dark:bg-slate-800/60 dark:text-slate-100 dark:shadow-slate-950/40">
        <div className="markdown">
          <Markdown
            remarkPlugins={[remarkGfm]}
            components={{
              table: ({ node, ...props }) => (
                <div className="my-2 max-w-full overflow-x-auto rounded-lg border border-slate-200 dark:border-white/10">
                  <table className="min-w-full" {...props} />
                </div>
              ),
            }}
          >
            {normalizeMarkdownTables(message.content)}
          </Markdown>
        </div>
        <ToolCallTrace toolCalls={message.tool_calls ?? []} />
        {message.execution_time_ms !== undefined && (
          <div>
            <ExecutionTimeBadge ms={message.execution_time_ms} />
          </div>
        )}
      </div>
    </div>
  )
}

function Avatar({ role }: { role: 'user' | 'assistant' }) {
  return (
    <div
      className={`mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg text-xs font-bold ${
        role === 'user'
          ? 'bg-slate-200 text-slate-500 dark:bg-slate-700 dark:text-slate-300'
          : 'bg-gradient-to-br from-indigo-500 to-violet-600 text-white'
      }`}
    >
      {role === 'user' ? 'OP' : 'AI'}
    </div>
  )
}

function Dot({ delay }: { delay: string }) {
  return (
    <span
      className="size-2 animate-bounce rounded-full bg-slate-300 dark:bg-slate-400"
      style={{ animationDelay: delay }}
    />
  )
}