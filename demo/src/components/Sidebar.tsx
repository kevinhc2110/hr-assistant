import { useEffect, useState } from 'react'
import type { Conversation } from '../types'

interface Props {
  activeId: string | null
  onSelect: (id: string) => void
  onUploadClick: () => void
  open: boolean
  onClose: () => void
}

export function Sidebar({ activeId, onSelect, onUploadClick, open, onClose }: Props) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchConvs = async () => {
      try {
        const res = await fetch('/chat/conversations?user_id=00000000-0000-0000-0000-000000000000')
        if (res.ok) setConversations(await res.json())
      } catch { /* ignore */ }
      finally { setLoading(false) }
    }
    fetchConvs()
  }, [])

  return (
    <>
      {open && <div className="fixed inset-0 bg-black/30 z-20 md:hidden" onClick={onClose} />}

      <aside className={`fixed md:static inset-y-0 left-0 z-30 w-72 bg-white border-r border-gray-200 flex flex-col transform transition-transform md:transform-none ${open ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        <div className="p-4 border-b border-gray-200">
          <button
            onClick={onUploadClick}
            className="w-full flex items-center gap-2 rounded-xl border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
              <path fillRule="evenodd" d="M10.5 3.75a6 6 0 0 0-5.98 6.496A5.25 5.25 0 0 0 6.75 20.25H18a4.5 4.5 0 0 0 2.206-8.423 3.75 3.75 0 0 0-4.133-4.303A6.001 6.001 0 0 0 10.5 3.75Z" clipRule="evenodd" />
            </svg>
            Subir documento
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-3">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 px-2">Conversaciones</h3>

          {loading && (
            <div className="flex justify-center py-8">
              <div className="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
            </div>
          )}

          {!loading && conversations.length === 0 && (
            <p className="text-sm text-gray-400 text-center py-8">Sin conversaciones aún</p>
          )}

          {conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => onSelect(conv.id)}
              className={`w-full text-left rounded-xl px-3 py-2.5 text-sm mb-1 transition-colors ${
                conv.id === activeId
                  ? 'bg-indigo-50 text-indigo-700 font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 flex-shrink-0 text-gray-400">
                  <path d="M4.913 2.658c2.275-.714 4.706-.121 6.537.918 1.763.998 3.04 2.62 3.454 4.478.526 2.365-.173 4.726-1.642 6.344a.75.75 0 0 0 .203 1.192l3.195 1.776a.75.75 0 0 0 .713-.011l2.745-1.57a.75.75 0 0 0 .266-1.048L18.98 12.53a.75.75 0 0 0-.083-.855 7.642 7.642 0 0 1-.772-5.36c.48-2.164-.555-4.412-2.337-5.618-1.907-1.29-4.506-1.84-6.858-.797-.526.233-1.339.624-1.339 1.351 0 .367.146.702.384.943a.75.75 0 0 0 .636.236Z" />
                </svg>
                <span className="truncate">{new Date(conv.created_at).toLocaleDateString('es-MX', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}</span>
              </div>
            </button>
          ))}
        </div>
      </aside>
    </>
  )
}
