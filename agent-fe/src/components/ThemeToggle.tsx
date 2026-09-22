import { Moon, Sun } from 'lucide-react'
import { useEffect } from 'react'
import { useUiStore } from '../store/uiStore'

export default function ThemeToggle({ className = '' }: { className?: string }) {
  const theme = useUiStore((s) => s.theme)
  const toggleTheme = useUiStore((s) => s.toggleTheme)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    try {
      localStorage.setItem('theme', theme)
    } catch {
      // storage unavailable — theme just won't persist
    }
  }, [theme])

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={`rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 dark:text-slate-400 dark:hover:bg-white/5 dark:hover:text-white ${className}`}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
    >
      {theme === 'dark' ? <Sun className="size-4" /> : <Moon className="size-4" />}
    </button>
  )
}