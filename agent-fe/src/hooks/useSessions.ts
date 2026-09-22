import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'
import { createSession, deleteSession, listSessions } from '../api/client'
import type { Session } from '../api/types'
import { useUiStore } from '../store/uiStore'

export const sessionKeys = {
  all: ['sessions'] as const,
  detail: (id: string) => ['sessions', id] as const,
}

export function useSessions() {
  return useQuery({
    queryKey: sessionKeys.all,
    queryFn: () => listSessions(),
  })
}

export function useCreateSession() {
  const qc = useQueryClient()
  const setActiveSession = useUiStore((s) => s.setActiveSession)
  return useMutation({
    mutationFn: createSession,
    onSuccess: (session: Session) => {
      qc.invalidateQueries({ queryKey: sessionKeys.all })
      setActiveSession(session.session_id)
    },
  })
}

export function useDeleteSession() {
  const qc = useQueryClient()
  const { activeSessionId, setActiveSession } = useUiStore()
  return useMutation({
    mutationFn: deleteSession,
    onSuccess: (_data, deletedId) => {
      qc.removeQueries({ queryKey: sessionKeys.detail(deletedId) })
      qc.invalidateQueries({ queryKey: sessionKeys.all })
      if (activeSessionId === deletedId) setActiveSession(null)
    },
  })
}