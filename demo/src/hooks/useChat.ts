import { useCallback, useRef, useState } from 'react'
import type { Message, WsMessage } from '../types'

export function useChat() {
  const ws = useRef<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [streamingId, setStreamingId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const convIdRef = useRef<string | null>(null)
  const accumulatedRef = useRef('')

  const onChunkRef = useRef<(text: string) => void>(() => {})
  const onDoneRef = useRef<(convId: string) => void>(() => {})
  const onErrorRef = useRef<(msg: string) => void>(() => {})

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return

    setConnectionError(null)
    setStreamingId(null)

    const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
    const url = `${protocol}://${location.host}/chat/ws`
    const socket = new WebSocket(url)

    socket.onopen = () => {
      setConnected(true)
      setConnectionError(null)
    }

    socket.onmessage = (event) => {
      try {
        const data: WsMessage = JSON.parse(event.data)
        switch (data.type) {
          case 'conversation_created': {
            const id = data.conversation_id ?? ''
            convIdRef.current = id
            setConversationId(id)
            break
          }
          case 'chunk':
            onChunkRef.current(data.content ?? '')
            break
          case 'done':
            onDoneRef.current(convIdRef.current ?? '')
            break
          case 'error':
            onErrorRef.current(data.message ?? 'Error desconocido')
            break
        }
      } catch {
        console.error('WS: error parsing message', event.data)
      }
    }

    socket.onclose = (event) => {
      setConnected(false)
      if (!event.wasClean) {
        setConnectionError('Conexión perdida')
      }
    }

    socket.onerror = () => {
      setConnected(false)
      setConnectionError('Error de conexión')
    }

    ws.current = socket
  }, [])

  const startStream = useCallback(() => {
    const tempId = crypto.randomUUID()
    setStreamingId(tempId)
    accumulatedRef.current = ''

    onChunkRef.current = (chunk) => {
      accumulatedRef.current += chunk
      setMessages((prev) =>
        prev.map((m) => (m.id === tempId ? { ...m, content: accumulatedRef.current } : m)),
      )
    }

    onDoneRef.current = () => {
      setStreamingId(null)
    }

    onErrorRef.current = (msg) => {
      setMessages((prev) =>
        prev.map((m) => (m.id === tempId ? { ...m, content: `Error: ${msg}` } : m)),
      )
      setStreamingId(null)
    }

    return tempId
  }, [])

  const sendWs = useCallback(
    (text: string) => {
      const userMsg: Message = {
        id: crypto.randomUUID(),
        role: 'user',
        content: text,
        created_at: new Date().toISOString(),
      }
      const tempId = startStream()
      const assistantMsg: Message = {
        id: tempId,
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, userMsg, assistantMsg])

      if (ws.current?.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({ message: text }))
      }
    },
    [startStream],
  )

  const loadConversation = useCallback(async (id: string) => {
    setLoading(true)
    setConversationId(id)
    convIdRef.current = id
    if (ws.current) {
      ws.current.close()
      ws.current = null
    }
    setConnected(false)
    setStreamingId(null)

    try {
      const res = await fetch(`/chat/messages?conversation_id=${id}`)
      if (res.ok) {
        const data: Message[] = await res.json()
        setMessages(data.reverse())
      }
    } catch {
      /* ignore */
    } finally {
      setLoading(false)
    }
    connect()
  }, [connect])

  const sendRest = useCallback(
    async (text: string) => {
      const cid = convIdRef.current
      if (!cid) return

      const userMsg: Message = {
        id: crypto.randomUUID(),
        role: 'user',
        content: text,
        created_at: new Date().toISOString(),
      }
      const tempId = crypto.randomUUID()
      const assistantMsg: Message = {
        id: tempId,
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, userMsg, assistantMsg])
      setStreamingId(tempId)

      try {
        const res = await fetch('/chat/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, conversation_id: cid }),
        })
        if (res.ok) {
          const data = await res.json()
          setMessages((prev) =>
            prev.map((m) => (m.id === tempId ? { ...m, content: data.answer } : m)),
          )
        } else {
          setMessages((prev) =>
            prev.map((m) => (m.id === tempId ? { ...m, content: 'Error del servidor' } : m)),
          )
        }
      } catch {
        setMessages((prev) =>
          prev.map((m) => (m.id === tempId ? { ...m, content: 'Error de conexión' } : m)),
        )
      } finally {
        setStreamingId(null)
      }
    },
    [],
  )

  const send = useCallback(
    (text: string) => {
      if (ws.current?.readyState === WebSocket.OPEN) {
        sendWs(text)
      } else {
        sendRest(text)
      }
    },
    [sendWs, sendRest],
  )

  return {
    connect,
    send,
    loadConversation,
    connected,
    connectionError,
    conversationId,
    messages,
    streamingId,
    loading,
  }
}
