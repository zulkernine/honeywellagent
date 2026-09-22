export interface Session {
  session_id: string
  title: string
  user_id: string
  created_at: string
  updated_at: string
}

export interface ToolCall {
  tool_name: string
  args: Record<string, unknown>
  result_summary: string
}

export interface Message {
  session_id: string
  role: 'user' | 'assistant'
  content: string
  tool_calls?: ToolCall[]
  execution_time_ms?: number
  created_at: string
}

export interface ChatRequest {
  message: string
}

export interface ChatResponse {
  session_id: string
  answer: string
  tool_calls: ToolCall[]
  execution_time_ms: number
}

export interface SessionDetail {
  session: Session
  messages: ChatMessage[]
}

export type ChatMessage = Message & {
  id: string
  pending?: boolean
}