import { create } from 'zustand'

type Theme = 'light' | 'dark'

function initialTheme(): Theme {
  try {
    return localStorage.getItem('theme') === 'dark' ? 'dark' : 'light'
  } catch {
    return 'light'
  }
}

interface UiState {
  activeSessionId: string | null
  sidebarOpen: boolean
  theme: Theme
  drafts: Record<string, string>
  setActiveSession: (id: string | null) => void
  setSidebarOpen: (open: boolean) => void
  toggleTheme: () => void
  setDraft: (sessionId: string, text: string) => void
  clearDraft: (sessionId: string) => void
}

export const useUiStore = create<UiState>()((set) => ({
  activeSessionId: null,
  sidebarOpen: false,
  theme: initialTheme(),
  drafts: {},
  setActiveSession: (id) => set({ activeSessionId: id }),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleTheme: () =>
    set((s) => ({ theme: s.theme === 'dark' ? 'light' : 'dark' })),
  setDraft: (sessionId, text) =>
    set((s) => ({ drafts: { ...s.drafts, [sessionId]: text } })),
  clearDraft: (sessionId) =>
    set((s) => {
      const drafts = { ...s.drafts }
      delete drafts[sessionId]
      return { drafts }
    }),
}))