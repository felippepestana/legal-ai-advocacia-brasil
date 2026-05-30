import { useCallback, useEffect, useState } from 'react'
import { ClipboardList, Download, KeyRound, Loader2, RefreshCw, ShieldCheck } from 'lucide-react'
import { api, getStoredApiKey, setStoredApiKey } from '../api/client'
import { Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui'

const OPERATION_LABELS = {
  document_enhance: 'Análise documental',
  search_synthesis: 'Síntese de pesquisa',
  assistant_chat: 'Assistente',
  document_generation: 'Geração de peça',
  generate: 'Geração IA',
  unit_test: 'Teste',
}

function formatTs(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('pt-BR')
  } catch {
    return iso
  }
}

export default function AuditPanel({ health }) {
  const [apiKey, setApiKey] = useState(getStoredApiKey())
  const [events, setEvents] = useState([])
  const [tenantId, setTenantId] = useState('')
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [error, setError] = useState('')

  const loadAudit = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const data = await api.auditRecent(30)
      setEvents(data.events || [])
      setTenantId(data.tenant_id || '')
    } catch (err) {
      setError(err.message || 'Erro ao carregar auditoria')
      setEvents([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadAudit()
  }, [loadAudit])

  function saveApiKey() {
    setStoredApiKey(apiKey.trim())
    loadAudit()
  }

  async function exportCsv() {
    setExporting(true)
    setError('')
    try {
      await api.auditExportCsv(500)
    } catch (err) {
      setError(err.message || 'Erro ao exportar CSV')
    } finally {
      setExporting(false)
    }
  }

  const successCount = events.filter((e) => e.success).length
  const failCount = events.length - successCount

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle icon={KeyRound}>Credenciais do escritório</CardTitle>
          <CardDescription>
            Necessário quando a API exige autenticação multi-tenant (header X-API-Key).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <label className="flex-1 text-sm">
              <span className="mb-1 block font-medium text-slate-700">API Key</span>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="dev-demo-key-change-me"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </label>
            <Button onClick={saveApiKey}>Salvar e atualizar</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <CardTitle icon={ClipboardList}>Auditoria de consultas IA</CardTitle>
              <CardDescription>
                Registros do tenant atual — sem conteúdo de prompts (LGPD). Tenant:{' '}
                <strong>{tenantId || 'public'}</strong>
              </CardDescription>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="outline" onClick={loadAudit} disabled={loading}>
                {loading ? (
                  <Loader2 className="mr-2 inline h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="mr-2 inline h-4 w-4" />
                )}
                Atualizar
              </Button>
              <Button variant="outline" onClick={exportCsv} disabled={exporting || events.length === 0}>
                {exporting ? (
                  <Loader2 className="mr-2 inline h-4 w-4 animate-spin" />
                ) : (
                  <Download className="mr-2 inline h-4 w-4" />
                )}
                Exportar CSV
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex flex-wrap gap-2">
            <Badge tone="default">{events.length} eventos</Badge>
            <Badge tone="success">{successCount} ok</Badge>
            {failCount > 0 && <Badge tone="danger">{failCount} falhas</Badge>}
            {health?.sentry_enabled && (
              <Badge tone="info">
                <ShieldCheck className="mr-1 inline h-3 w-3" />
                Sentry
              </Badge>
            )}
            {health?.structured_logging && (
              <Badge tone="info">Logs JSON / Cloud Logging</Badge>
            )}
            {health?.redis_connected && (
              <Badge tone="info">Redis (cache + rate limit)</Badge>
            )}
            {health?.slack_alerts_enabled && (
              <Badge tone="info">Alertas Slack</Badge>
            )}
          </div>

          {error && (
            <p className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
          )}

          {events.length === 0 && !loading && !error && (
            <p className="text-sm text-slate-500">
              Nenhum evento registrado hoje. Use análise, pesquisa ou assistente com IA
              enriquecida para gerar registros.
            </p>
          )}

          {events.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[640px] text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-xs uppercase text-slate-500">
                    <th className="py-2 pr-4">Horário</th>
                    <th className="py-2 pr-4">Operação</th>
                    <th className="py-2 pr-4">Modelo</th>
                    <th className="py-2 pr-4">Latência</th>
                    <th className="py-2 pr-4">Tokens (chars)</th>
                    <th className="py-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {[...events].reverse().map((event, idx) => (
                    <tr key={`${event.ts}-${idx}`} className="border-b border-slate-100">
                      <td className="py-2 pr-4 whitespace-nowrap text-slate-600">
                        {formatTs(event.ts)}
                      </td>
                      <td className="py-2 pr-4">
                        {OPERATION_LABELS[event.operation] || event.operation}
                      </td>
                      <td className="py-2 pr-4 text-slate-600">
                        {event.backend}/{event.model}
                      </td>
                      <td className="py-2 pr-4">{event.latency_ms} ms</td>
                      <td className="py-2 pr-4 text-slate-500">
                        in {(event.user_chars || 0) + (event.system_chars || 0)} · out{' '}
                        {event.output_chars || 0}
                      </td>
                      <td className="py-2">
                        {event.success ? (
                          <Badge tone="success">OK</Badge>
                        ) : (
                          <Badge tone="danger" title={event.error}>
                            Erro
                          </Badge>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
