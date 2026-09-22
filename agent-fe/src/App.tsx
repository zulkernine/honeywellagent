import { Menu } from 'lucide-react'
import ChatPanel from './components/ChatPanel'
import Sidebar from './components/Sidebar'
import ThemeToggle from './components/ThemeToggle'
import { useSessions } from './hooks/useSessions'
import { useUiStore } from './store/uiStore'

export default function App() {
  const activeSessionId = useUiStore((s) => s.activeSessionId)
  const setSidebarOpen = useUiStore((s) => s.setSidebarOpen)
  const { data: sessions } = useSessions()
  const activeSession = sessions?.find((s) => s.session_id === activeSessionId)

  return (
    <div className="flex h-screen overflow-hidden bg-white text-slate-800 dark:bg-slate-950 dark:text-slate-100">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Mobile top bar */}
        <header className="flex items-center gap-2 border-b border-slate-200 bg-white/80 px-3 py-2.5 backdrop-blur lg:hidden dark:border-white/10 dark:bg-slate-900/80">
          <button
            type="button"
            onClick={() => setSidebarOpen(true)}
            className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:text-slate-400 dark:hover:bg-white/5 dark:hover:text-white"
            aria-label="Open sidebar"
          >
            <Menu className="size-5" />
          </button>
          <span className="min-w-0 flex-1 truncate text-sm font-medium text-slate-700 dark:text-slate-200">
            {activeSession?.title ?? 'AI Operations Agent'}
          </span>
          <ThemeToggle />
        </header>

        {activeSessionId ? (
          <ChatPanel sessionId={activeSessionId} />
        ) : (
          <WelcomeScreen />
        )}
      </div>
    </div>
  )
}

function WelcomeScreen() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-6 text-center">
      <h1 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">
        AI Operations Agent
      </h1>
      <p className="mt-2 max-w-md text-sm text-slate-500 dark:text-slate-400">
        Select a conversation from the sidebar, or start a new chat to query
        and act on your enterprise certificate data.
      </p>
    </div>
  )
}