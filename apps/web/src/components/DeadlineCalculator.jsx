import { useState } from 'react'
import { Calendar } from 'lucide-react'
import { api } from '../api/client'
import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui'

const DEADLINE_TYPES = [
  { id: 'contestacao', label: 'Contestação (15 dias úteis)' },
  { id: 'recurso', label: 'Recurso (15 dias úteis)' },
  { id: 'replicas', label: 'Réplica (10 dias úteis)' },
  { id: 'manifestacao', label: 'Manifestação (15 dias úteis)' },
]

export default function DeadlineCalculator() {
  const [eventDate, setEventDate] = useState('')
  const [deadlineType, setDeadlineType] = useState('contestacao')
  const [courtType, setCourtType] = useState('estadual')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const calculate = async () => {
    if (!eventDate) {
      setError('Informe a data do evento (citação/intimação).')
      return
    }
    setLoading(true)
    setError('')
    try {
      const data = await api.calculateDeadline(eventDate, deadlineType, courtType)
      setResult(data)
    } catch (e) {
      setError(e.message)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="max-w-xl">
      <CardHeader>
        <CardTitle icon={Calendar}>Prazos processuais</CardTitle>
        <CardDescription>Contagem em dias úteis com feriados nacionais (BR)</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="text-sm">
            Data do evento
            <input
              type="date"
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
              value={eventDate}
              onChange={(e) => setEventDate(e.target.value)}
            />
          </label>
          <label className="text-sm">
            Tribunal
            <select
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
              value={courtType}
              onChange={(e) => setCourtType(e.target.value)}
            >
              <option value="estadual">Estadual</option>
              <option value="federal">Federal</option>
              <option value="trabalhista">Trabalhista</option>
            </select>
          </label>
        </div>
        <label className="block text-sm">
          Tipo de prazo
          <select
            className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
            value={deadlineType}
            onChange={(e) => setDeadlineType(e.target.value)}
          >
            {DEADLINE_TYPES.map((t) => (
              <option key={t.id} value={t.id}>
                {t.label}
              </option>
            ))}
          </select>
        </label>
        <Button onClick={calculate} disabled={loading}>
          {loading ? 'Calculando...' : 'Calcular vencimento'}
        </Button>
        {error && <p className="text-sm text-red-600">{error}</p>}
        {result && (
          <div className="rounded-lg bg-indigo-50 p-4 text-sm">
            <p className="text-lg font-semibold text-indigo-900">
              Vencimento: {new Date(result.calculated_date + 'T12:00:00').toLocaleDateString('pt-BR')}
            </p>
            <p className="mt-1 text-indigo-700">{result.business_days} dias úteis</p>
            <p className="mt-2 text-xs text-indigo-600">{result.calculation_details}</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
