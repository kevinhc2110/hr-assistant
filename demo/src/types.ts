export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface Conversation {
  id: string
  created_at: string
}

export interface WsMessage {
  type: 'conversation_created' | 'chunk' | 'done' | 'error'
  conversation_id?: string
  content?: string
  message?: string
}
