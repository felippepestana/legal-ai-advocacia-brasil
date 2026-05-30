import { useEffect, useState } from 'react'
import { BarChart3, Loader2 } from 'lucide-react'
import { api } from '../api/client'
import { Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui'

function MetricBlock({ label, value }) {
  if (value == null) return null
  const display =
    typeof value === 'number'
      ? Number.isInteger(value)
        ? value.toLocaleString('pt-BR')
        : value.toLocaleString('pt-BR', { maximumFractionDigits: 1 })
      : String(value)
  return (
    <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-semibold text-slate-900">{display}</p>
    </div>
  )
}

function DictMetrics({ title, data }) {
  if (!data || typeof data !== 'object') return null
  const entries = Object.entries(data)
  if (!entries.length) return null
  return (
    <div className="mt-4">
      <h3 className="mb-2 text-sm font-medium text-slate-700">{title}</h3>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {entries.map(([key, val]) => (
          <MetricBlock key={key} label={key.replace(/_/g, ' ')} value={val} />
        ))}
      </div>
    </div>
  )
}

export default function LegalAnalytics() {
  const [types, setTypes] = useState([])
  const [analysisType, setAnalysisType] = useState('performance')
  const [numCases, setNumCases] = useState(300)
  const [exportCharts, setExportCharts] = useState(false)
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .listAnalyticsTypes()
      .then((data) => setTypes(data.types || []))
      .catch(() => setTypes([]))
  }, [])

  async function handleRun() {
    setLoading(true)
    setError('')
    try {
      const data = await api.runAnalytics(analysisType, numCases, exportCharts)
      setReport(data)
    } catch (err) {
      setError(err.message)
      setReport(null)
    } finally {
      setLoading(false)
    }
  }

  const metrics = report?.metrics || {}

  return (
    <Card>
      <CardHeader>
        <CardTitle icon={BarChart3}>Analytics jurídico</CardTitle>
        <CardDescription>
          Indicadores de performance, projeções e financeiro com dados sintéticos de demonstração.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-4">
          <label className="block text-sm">
            <span className="text-slate-600">Tipo de análise</span>
            <select
              className="mt-1 block w-full min-w-[200px] rounded-lg border border-slate-300 px-3 py-2"
              value={analysisType}
              onChange={(e) => setAnalysisType(e.target.value)}
            >
              {(types.length ? types : [{ id: 'performance', label: 'Performance' }]).map((t) => (
                <option key={t.id} value={t.id}>
                  {t.label}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm">
            <span className="text-slate-600">Casos (amostra)</span>
            <input
              type="number"
              min={50}
              max={2000}
              className="mt-1 block w-32 rounded-lg border border-slate-300 px-3 py-2"
              value={numCases}
              onChange={(e) => setNumCases(Number(e.target.value))}
            />
          </label>
          <label className="flex items-end gap-2 pb-2 text-sm text-slate-600">
            <input
              type="checkbox"
              checked={exportCharts}
              onChange={(e) => setExportCharts(e.target.checked)}
            />
            Exportar gráficos PNG
          </label>
          <div className="flex items-end">
            <Button onClick={handleRun} disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 inline h-4 w-4 animate-spin" />
                  Gerando…
                </>
              ) : (
                'Gerar relatório'
              )}
            </Button>
          </div>
        </div>

        {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

        {report && (
          <div className="mt-6 space-y-4 border-t border-slate-100 pt-6">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="text-base font-semibold text-slate-900">{report.title}</h3>
              <Badge tone="default">{report.analysis_type}</Badge>
              {report.metadata?.synthetic_data && (
                <Badge tone="warning">Dados sintéticos</Badge>
              )}
            </div>

            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {metrics.overall_success_rate != null && (
                <MetricBlock label="Taxa de sucesso geral (%)" value={metrics.overall_success_rate} />
              )}
              {metrics.overall_avg_duration != null && (
                <MetricBlock label="Duração média (dias)" value={metrics.overall_avg_duration} />
              )}
              {metrics.total_revenue != null && (
                <MetricBlock label="Receita total (R$)" value={metrics.total_revenue} />
              )}
            </div>

            <DictMetrics title="Por área — sucesso (%)" data={metrics.success_rate_by_area} />
            <DictMetrics title="Por área — duração média (dias)" data={metrics.avg_duration_by_area} />
            <DictMetrics title="Por área — receita" data={metrics.revenue_by_area} />

            {report.insights?.length > 0 && (
              <div>
                <h3 className="mb-2 text-sm font-medium text-slate-700">Insights</h3>
                <ul className="list-inside list-disc space-y-1 text-sm text-slate-600">
                  {report.insights.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            )}

            {report.recommendations?.length > 0 && (
              <div>
                <h3 className="mb-2 text-sm font-medium text-slate-700">Recomendações</h3>
                <ul className="list-inside list-disc space-y-1 text-sm text-slate-600">
                  {report.recommendations.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            )}

            {report.chart_urls?.length > 0 && (
              <div>
                <h3 className="mb-2 text-sm font-medium text-slate-700">Gráficos</h3>
                <div className="grid gap-4 sm:grid-cols-2">
                  {report.chart_urls.map((chart) => (
                    <figure key={chart.name} className="rounded-lg border border-slate-200 p-2">
                      <img
                        src={chart.url}
                        alt={chart.name}
                        className="h-auto w-full rounded"
                      />
                      <figcaption className="mt-1 text-xs text-slate-500">{chart.name}</figcaption>
                    </figure>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
