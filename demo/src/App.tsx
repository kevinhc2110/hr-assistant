import { useEffect, useRef, useState } from 'react'
import { useChat } from './hooks/useChat'
import { Sidebar } from './components/Sidebar'
import { ChatInput } from './components/ChatInput'
import { MessageBubble } from './components/MessageBubble'
import { UploadModal } from './components/UploadModal'

export default function App() {
  const [uploadOpen, setUploadOpen] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  const {
    connect,
    send,
    loadConversation,
    connected,
    connectionError,
    conversationId,
    messages,
    streamingId,
    loading,
  } = useChat()

  useEffect(() => {
    const init = async () => {
      try {
        const res = await fetch(
          '/chat/conversations?user_id=00000000-0000-0000-0000-000000000000',
        )
        if (res.ok) {
          const convs = await res.json()
          if (convs.length > 0) {
            await loadConversation(convs[0].id)
            return
          }
        }
      } catch {
        /* ignore */
      }
      connect()
    }
    init()
  }, [connect, loadConversation])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="h-dvh flex overflow-hidden bg-gray-50">
      <Sidebar
        activeId={conversationId}
        onSelect={loadConversation}
        onUploadClick={() => setUploadOpen(true)}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex-1 flex flex-col min-w-0">
        <header className="flex items-center gap-3 border-b border-gray-200 bg-white px-4 py-3">
          <button
            onClick={() => setSidebarOpen((v) => !v)}
            className="md:hidden p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6 text-gray-700">
              <path fillRule="evenodd" d="M3 6.75A.75.75 0 0 1 3.75 6h16.5a.75.75 0 0 1 0 1.5H3.75A.75.75 0 0 1 3 6.75ZM3 12a.75.75 0 0 1 .75-.75h16.5a.75.75 0 0 1 0 1.5H3.75A.75.75 0 0 1 3 12Zm0 5.25a.75.75 0 0 1 .75-.75h16.5a.75.75 0 0 1 0 1.5H3.75a.75.75 0 0 1-.75-.75Z" clipRule="evenodd" />
            </svg>
          </button>

          <div className="flex items-center gap-2.5 flex-1">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white text-xs font-bold">
              HR
            </div>
            <div className="flex-1">
              <h1 className="text-sm font-semibold text-gray-900">HR Assistant</h1>
              <p className="text-xs">
                {connectionError ? (
                  <span className="text-red-500">{connectionError}</span>
                ) : connected ? (
                  <span className="text-green-500">Conectado</span>
                ) : conversationId ? (
                  <span className="text-amber-500">Conversación existente</span>
                ) : (
                  <span className="text-gray-400">Desconectado</span>
                )}
              </p>
            </div>
            {connectionError && (
              <button
                onClick={connect}
                className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
              >
                Reconectar
              </button>
            )}
          </div>
        </header>

        <div className="flex-1 overflow-y-auto px-4 py-6">
          {loading && (
            <div className="flex justify-center py-12">
              <div className="w-6 h-6 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
            </div>
          )}

          {!loading && messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 bg-indigo-100 rounded-2xl flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-8 h-8 text-indigo-600">
                  <path d="M4.913 2.658c2.275-.714 4.706-.121 6.537.918 1.763.998 3.04 2.62 3.454 4.478.526 2.365-.173 4.726-1.642 6.344a.75.75 0 0 0 .203 1.192l3.195 1.776a.75.75 0 0 0 .713-.011l2.745-1.57a.75.75 0 0 0 .266-1.048L18.98 12.53a.75.75 0 0 0-.083-.855 7.642 7.642 0 0 1-.772-5.36c.48-2.164-.555-4.412-2.337-5.618-1.907-1.29-4.506-1.84-6.858-.797-.526.233-1.339.624-1.339 1.351 0 .367.146.702.384.943a.75.75 0 0 0 .636.236Z" />
                </svg>
              </div>
              <h2 className="text-lg font-semibold text-gray-700 mb-1">HR Assistant</h2>
              <p className="text-sm text-gray-400 max-w-sm">
                Pregunta sobre políticas, vacaciones, beneficios y más. Los documentos subidos se usan como contexto para responder.
              </p>
            </div>
          )}

          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} isStreaming={msg.id === streamingId} />
          ))}

          <div ref={bottomRef} />
        </div>

        <ChatInput onSend={send} disabled={!connected && !conversationId} />
      </div>

      <UploadModal open={uploadOpen} onClose={() => setUploadOpen(false)} />
    </div>
  )
}
