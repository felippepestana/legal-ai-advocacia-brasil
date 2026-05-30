import { useState } from 'react'
import { Search, Sparkles } from 'lucide-react'
import { api } from '../api/client'
import { Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui'

const SEARCH_TYPES = [
  { value: 'mista', label: 'Mista' },
  { value: 'jurisprudencia', label: 'Jurisprudência' },
  { value: 'legislacao', label: 'Legislação' },
]

export default function LegalSearch({ geminiAvailable }) {
  const [query, setQuery] = useState('danos morais negativação indevida')
  const [searchType, setSearchType] = useState('mista')
  const [useGemini, setUseGemini] = useState(false)
  const [useExternal, setUseExternal] = useState(true)
  const [tribunals, setTribunals] = useState('stj,stf,tjsp')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const run = async () => {
    if (query.trim().length < 3) {
      setError('Informe pelo menos 3 caracteres.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const tribunalList = tribunals
        .split(',')
        .map((t) => t.trim().toLowerCase())
        .filter(Boolean)
      const data = await api.searchLegal(
        query,
        searchType,
        useGemini,
        useExternal,
        tribunalList,
      )
      setResult(data)
    } catch (e) {
      setError(e.message)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle icon={Search}>Pesquisa normativa</CardTitle>
          <CardDescription>
            DataJud (CNJ), Senado/LexML e base local; STJ textual com token opcional
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <input
            className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ex.: horas extras habitualidade"
          />
          <select
            className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
            value={searchType}
            onChange={(e) => setSearchType(e.target.value)}
          >
            {SEARCH_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
          <label className="flex items-center gap-2 text-sm text-slate-600">
            <input
              type="checkbox"
              checked={useExternal}
              onChange={(e) => setUseExternal(e.target.checked)}
            />
            Fontes públicas (DataJud + legislação Senado/LexML)
          </label>
          <input
            className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
            value={tribunals}
            onChange={(e) => setTribunals(e.target.value)}
            placeholder="Tribunais DataJud: stj,stf,tjsp"
            disabled={!useExternal}
          />
          {geminiAvailable && (
            <label className="flex items-center gap-2 text-sm text-slate-600">
              <input type="checkbox" checked={useGemini} onChange={(e) => setUseGemini(e.target.checked)} />
              <Sparkles className="h-4 w-4 text-amber-500" />
              Síntese com Gemini
            </label>
          )}
          <Button onClick={run} disabled={loading}>
            {loading ? 'Pesquisando...' : 'Pesquisar'}
          </Button>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Resultados</CardTitle>
          <CardDescription>{result?.disclaimer}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!result && <p className="text-sm text-slate-400">Execute uma pesquisa</p>}
          {result && (
            <>
              <div className="flex flex-wrap gap-2 text-xs">
                <Badge>{result.total_results} resultado(s)</Badge>
                <Badge tone="success">{result.search_time_ms} ms</Badge>
                {result.sources?.providers?.map((p) => (
                  <Badge key={p} tone="success">
                    {p}
                  </Badge>
                ))}
                {result.synthesis && <Badge tone="warning">Síntese Gemini</Badge>}
              </div>
              {result.sources?.warnings?.length > 0 && (
                <ul className="text-xs text-amber-800">
                  {result.sources.warnings.map((w) => (
                    <li key={w}>{w}</li>
                  ))}
                </ul>
              )}
              {result.synthesis && (
                <div className="rounded-lg bg-amber-50 p-3 text-sm text-amber-950 whitespace-pre-wrap">
                  {result.synthesis}
                </div>
              )}
              {result.suggestions?.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {result.suggestions.map((s) => (
                    <button
                      key={s}
                      type="button"
                      className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600 hover:bg-slate-200"
                      onClick={() => setQuery(s)}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
              <ul className="max-h-96 space-y-3 overflow-y-auto">
                {result.results.map((r) => (
                  <li key={r.id} className="rounded-lg border border-slate-200 p-3 text-sm">
                    <div className="font-semibold text-slate-800">{r.title}</div>
                    <div className="mt-1 text-xs text-slate-500">
                      {r.source}
                      {r.court ? ` · ${r.court}` : ''}
                      {r.relevance_score != null && ` · ${(r.relevance_score * 100).toFixed(0)}%`}
                      {r.metadata?.provider && ` · ${r.metadata.provider}`}
                    </div>
                    <p className="mt-2 line-clamp-4 text-slate-600">{r.content}</p>
                    {r.url && (
                      <a
                        href={r.url}
                        target="_blank"
                        rel="noreferrer"
                        className="mt-2 inline-block text-xs text-indigo-600 hover:underline"
                      >
                        Abrir fonte
                      </a>
                    )}
                  </li>
                ))}
              </ul>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
