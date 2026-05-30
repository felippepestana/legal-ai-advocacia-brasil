import { useEffect, useState } from 'react'
import { GitBranch, Play } from 'lucide-react'
import { api } from '../api/client'
import { Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui'

export default function WorkflowRunner() {
  const [templates, setTemplates] = useState([])
  const [templateId, setTemplateId] = useState('')
  const [name, setName] = useState('Workflow teste')
  const [workflowId, setWorkflowId] = useState('')
  const [executionId, setExecutionId] = useState('')
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.listWorkflowTemplates().then((r) => {
      const list = r.templates || []
      setTemplates(list)
      if (list[0]) setTemplateId(list[0].id)
    }).catch(() => {})
  }, [])

  useEffect(() => {
    if (!executionId) return undefined
    const poll = setInterval(async () => {
      try {
        const s = await api.getWorkflowExecution(executionId)
        setStatus(s)
        if (s.status === 'Concluído' || s.status === 'Falhou') {
          clearInterval(poll)
        }
      } catch {
        clearInterval(poll)
      }
    }, 800)
    return () => clearInterval(poll)
  }, [executionId])

  const createAndRun = async () => {
    setLoading(true)
    setError('')
    setStatus(null)
    setExecutionId('')
    try {
      const created = await api.createWorkflow(
        templateId,
        name,
        { client_id: 'demo', case_type: 'Cível' },
      )
      setWorkflowId(created.workflow_id)
      const exec = await api.executeWorkflow(created.workflow_id, { urgency: 'normal' })
      setExecutionId(exec.execution_id)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const selected = templates.find((t) => t.id === templateId)

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle icon={GitBranch}>Workflows jurídicos</CardTitle>
          <CardDescription>Automação de rotinas (petição, prazos, audiência…)</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <select
            className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
            value={templateId}
            onChange={(e) => setTemplateId(e.target.value)}
          >
            {templates.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
          {selected && <p className="text-xs text-slate-500">{selected.description}</p>}
          <input
            className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Nome do workflow"
          />
          <Button onClick={createAndRun} disabled={loading || !templateId}>
            <Play className="mr-2 h-4 w-4" />
            {loading ? 'Executando...' : 'Criar e executar'}
          </Button>
          {workflowId && (
            <p className="text-xs text-slate-500">Workflow: {workflowId.slice(0, 8)}…</p>
          )}
          {error && <p className="text-sm text-red-600">{error}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Status da execução</CardTitle>
        </CardHeader>
        <CardContent>
          {!status && <p className="text-sm text-slate-400">Aguardando execução</p>}
          {status && (
            <div className="space-y-3 text-sm">
              <div className="flex flex-wrap gap-2">
                <Badge tone={status.status === 'Concluído' ? 'success' : 'warning'}>
                  {status.status}
                </Badge>
                <Badge>{status.steps_completed} etapa(s)</Badge>
              </div>
              <p className="text-xs text-slate-500">
                Início: {status.start_time}
                {status.end_time && ` · Fim: ${status.end_time}`}
              </p>
              {status.errors?.length > 0 && (
                <ul className="text-xs text-red-600">
                  {status.errors.map((e, i) => (
                    <li key={i}>{e}</li>
                  ))}
                </ul>
              )}
              {status.step_results && (
                <pre className="max-h-64 overflow-auto rounded bg-slate-50 p-2 text-xs">
                  {JSON.stringify(status.step_results, null, 2)}
                </pre>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
