import { useEffect, useRef, useState } from 'react'
import { Bot, Send, Sparkles } from 'lucide-react'
import { api } from '../api/client'
import { Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui'

const LEVELS = [
  { value: 'advogado', label: 'Advogado' },
  { value: 'estagiario', label: 'Estagiário' },
  { value: 'cliente', label: 'Cliente (linguagem simples)' },
]

export default function AssistantChat({ geminiAvailable }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Olá. Sou o assistente do escritório. Posso orientar sobre prazos, conceitos jurídicos e uso da plataforma.',
    },
  ])
  const [input, setInput] = useState('')
  const [level, setLevel] = useState('advogado')
  const [useGemini, setUseGemini] = useState(false)
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const send = async () => {
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    setMessages((m) => [...m, { role: 'user', text }])
    setLoading(true)
    try {
      const res = await api.assistantChat(text, level, useGemini)
      setMessages((m) => [
        ...m,
        {
          role: 'assistant',
          text: res.answer,
          meta: res,
        },
      ])
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', text: `Erro: ${e.message}`, error: true }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="mx-auto max-w-3xl">
      <CardHeader>
        <CardTitle icon={Bot}>Assistente do escritório</CardTitle>
        <CardDescription>Orientação — não substitui advogado habilitado</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-3">
          <select
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            value={level}
            onChange={(e) => setLevel(e.target.value)}
          >
            {LEVELS.map((l) => (
              <option key={l.value} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
          {geminiAvailable && (
            <label className="flex items-center gap-2 text-sm text-slate-600">
              <input type="checkbox" checked={useGemini} onChange={(e) => setUseGemini(e.target.checked)} />
              <Sparkles className="h-4 w-4 text-amber-500" />
              Gemini
            </label>
          )}
        </div>

        <div className="h-96 space-y-3 overflow-y-auto rounded-lg border border-slate-200 bg-slate-50 p-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`rounded-lg px-3 py-2 text-sm ${
                msg.role === 'user'
                  ? 'ml-8 bg-indigo-600 text-white'
                  : msg.error
                    ? 'mr-8 bg-red-50 text-red-800'
                    : 'mr-8 bg-white text-slate-800 shadow-sm'
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.text}</div>
              {msg.meta?.follow_up_questions?.length > 0 && (
                <ul className="mt-2 list-inside list-disc text-xs opacity-80">
                  {msg.meta.follow_up_questions.slice(0, 3).map((q) => (
                    <li key={q}>{q}</li>
                  ))}
                </ul>
              )}
              {msg.meta?.metadata?.ai_enhanced && (
                <Badge tone="warning" className="mt-2">
                  Gemini
                </Badge>
              )}
            </div>
          ))}
          {loading && <p className="text-xs text-slate-400">Pensando...</p>}
          <div ref={bottomRef} />
        </div>

        <div className="flex gap-2">
          <input
            className="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send()}
            placeholder="Ex.: Qual o prazo para contestação?"
          />
          <Button onClick={send} disabled={loading}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
