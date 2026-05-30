import { useState } from 'react'
import { Scale } from 'lucide-react'
import { api } from '../api/client'
import { Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui'

export default function DocumentValidate() {
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const validate = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await api.validateDocument(text)
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
          <CardTitle icon={Scale}>Validação CPC — Petição inicial</CardTitle>
          <CardDescription>Checklist art. 319 CPC/2015</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <textarea
            className="min-h-[240px] w-full rounded-lg border border-slate-200 p-3 text-sm"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Cole a minuta da petição inicial..."
          />
          <Button onClick={validate} disabled={loading}>
            {loading ? 'Validando...' : 'Validar peça'}
          </Button>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Conformidade</CardTitle>
        </CardHeader>
        <CardContent>
          {!result && <p className="text-sm text-slate-400">Aguardando validação</p>}
          {result && (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <span className="text-3xl font-bold text-indigo-600">{result.compliance_score}%</span>
                <Badge tone={result.compliance_score >= 70 ? 'success' : 'warning'}>
                  {result.compliance_score >= 70 ? 'Adequado' : 'Revisar'}
                </Badge>
              </div>
              <ul className="max-h-96 space-y-2 overflow-y-auto text-sm">
                {result.itens?.map((item, i) => (
                  <li
                    key={i}
                    className={`rounded border p-2 ${
                      item.status === 'ok' ? 'border-emerald-200 bg-emerald-50' : 'border-amber-200 bg-amber-50'
                    }`}
                  >
                    <div className="font-medium">{item.requisito}</div>
                    <div className="text-xs text-slate-600">{item.trecho_ou_observacao}</div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
