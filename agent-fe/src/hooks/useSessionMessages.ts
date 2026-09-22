import { useQuery } from '@tanstack/react-query'
import { getSession } from '../api/client'
import type { ChatMessage } from '../api/types'
import { sessionKeys } from './useSessions'

export function useSessionMessages(sessionId: string | null) {
  return useQuery({
    queryKey: sessionKeys.detail(sessionId ?? 'none'),
    queryFn: () => getSession(sessionId!),
    enabled: sessionId !== null,
    select: (data) => ({
      session: data.session,
      messages: data.messages.map((m, i) => ({
        ...m,
        id: `s-${i}`,
      })) as ChatMessage[],
    }),
  })
}