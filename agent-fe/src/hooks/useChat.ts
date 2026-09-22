import { useMutation, useQueryClient } from '@tanstack/react-query'
import { postChat } from '../api/client'
import type { ChatMessage, SessionDetail } from '../api/types'
import { sessionKeys } from './useSessions'

export function useChat(sessionId: string | null) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (message: string) => {
      if (!sessionId) throw new Error('No active session.')
      return postChat(sessionId, { message })
    },
    onMutate: async (message: string) => {
      if (!sessionId) return
      await qc.cancelQueries({ queryKey: sessionKeys.detail(sessionId) })
      const previous = qc.getQueryData<SessionDetail>(
        sessionKeys.detail(sessionId),
      )
      const stamp = new Date().toISOString()
      const userMsg: ChatMessage = {
        id: `local-u-${stamp}`,
        session_id: sessionId,
        role: 'user',
        content: message,
        created_at: stamp,
      }
      const pendingMsg: ChatMessage = {
        id: `local-p-${stamp}`,
        session_id: sessionId,
        role: 'assistant',
        content: '',
        pending: true,
        created_at: stamp,
      }
      const base = previous ?? {
        session: {
          session_id: sessionId,
          title: 'New conversation',
          user_id: 'admin',
          created_at: stamp,
          updated_at: stamp,
        },
        messages: [] as ChatMessage[],
      }
      qc.setQueryData<SessionDetail>(sessionKeys.detail(sessionId), {
        ...base,
        messages: [...base.messages, userMsg, pendingMsg],
      })
      return { previous }
    },
    onError: (_err, _message, context) => {
      if (!sessionId) return
      if (context?.previous) {
        qc.setQueryData(sessionKeys.detail(sessionId), context.previous)
      }
      qc.invalidateQueries({ queryKey: sessionKeys.detail(sessionId) })
    },
    onSuccess: (response) => {
      if (!sessionId) return
      qc.setQueryData<SessionDetail>(sessionKeys.detail(sessionId), (data) => {
        if (!data) return data
        const assistantMsg: ChatMessage = {
          id: `local-a-${Date.now()}`,
          session_id: sessionId,
          role: 'assistant',
          content: response.answer,
          tool_calls: response.tool_calls,
          execution_time_ms: response.execution_time_ms,
          created_at: new Date().toISOString(),
        }
        // Replace the trailing pending placeholder with the real answer.
        const msgs = [...data.messages]
        const idx = msgs.findLastIndex((m) => m.pending)
        if (idx !== -1) msgs[idx] = assistantMsg
        else msgs.push(assistantMsg)
        return { ...data, messages: msgs }
      })
      // Session title changes after the first chat — refresh the sidebar.
      qc.invalidateQueries({ queryKey: sessionKeys.all })
    },
  })
}