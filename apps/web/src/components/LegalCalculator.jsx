import { useState } from 'react'
import { Calculator } from 'lucide-react'
import { api } from '../api/client'
import { Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui'

const CALC_TYPES = [
  {
    id: 'trabalhista/rescisao',
    area: 'trabalhista',
    subtype: 'rescisao',
    label: 'Rescisão trabalhista',
    fields: [
      { key: 'salario', label: 'Salário (R$)', type: 'number', default: '3000' },
      { key: 'data_admissao', label: 'Data admissão', type: 'date', default: '2022-01-15' },
      { key: 'data_demissao', label: 'Data demissão', type: 'date', default: '2024-09-15' },
      {
        key: 'tipo_rescisao',
        label: 'Tipo',
        type: 'select',
        options: [
          { value: 'sem_justa_causa', label: 'Sem justa causa' },
          { value: 'com_justa_causa', label: 'Com justa causa' },
          { value: 'pedido_demissao', label: 'Pedido de demissão' },
        ],
        default: 'sem_justa_causa',
      },
      {
        key: 'aviso_previo_trabalhado',
        label: 'Aviso prévio trabalhado',
        type: 'checkbox',
        default: false,
      },
    ],
  },
  {
    id: 'civil/danos_morais',
    area: 'civil',
    subtype: 'danos_morais',
    label: 'Danos morais',
    fields: [
      { key: 'valor_base', label: 'Valor base (R$)', type: 'number', default: '0', hint: '0 = salário mínimo ref.' },
      {
        key: 'gravidade',
        label: 'Gravidade',
        type: 'select',
        options: [
          { value: 'baixa', label: 'Baixa' },
          { value: 'media', label: 'Média' },
          { value: 'alta', label: 'Alta' },
        ],
        default: 'media',
      },
      {
        key: 'capacidade_economica',
        label: 'Capacidade econômica do réu',
        type: 'select',
        options: [
          { value: 'baixa', label: 'Baixa' },
          { value: 'media', label: 'Média' },
          { value: 'alta', label: 'Alta' },
        ],
        default: 'media',
      },
      {
        key: 'repercussao',
        label: 'Repercussão',
        type: 'select',
        options: [
          { value: 'local', label: 'Local' },
          { value: 'regional', label: 'Regional' },
          { value: 'nacional', label: 'Nacional' },
        ],
        default: 'local',
      },
    ],
  },
  {
    id: 'civil/correcao_monetaria',
    area: 'civil',
    subtype: 'correcao_monetaria',
    label: 'Correção monetária',
    fields: [
      { key: 'valor_principal', label: 'Valor principal (R$)', type: 'number', default: '10000' },
      { key: 'data_inicial', label: 'Data inicial', type: 'date', default: '2023-01-01' },
      { key: 'data_final', label: 'Data final', type: 'date', default: '2024-12-31' },
      {
        key: 'indice',
        label: 'Índice',
        type: 'select',
        options: [{ value: 'ipca', label: 'IPCA' }],
        default: 'ipca',
      },
    ],
  },
]

function defaultValues(calc) {
  const values = {}
  for (const f of calc.fields) {
    values[f.key] = f.default ?? ''
  }
  return values
}

function formatMoney(value) {
  const n = Number.parseFloat(value)
  if (Number.isNaN(n)) return value
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export default function LegalCalculator() {
  const [calcId, setCalcId] = useState(CALC_TYPES[0].id)
  const calc = CALC_TYPES.find((c) => c.id === calcId) ?? CALC_TYPES[0]
  const [form, setForm] = useState(() => defaultValues(CALC_TYPES[0]))
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const onCalcTypeChange = (id) => {
    const next = CALC_TYPES.find((c) => c.id === id) ?? CALC_TYPES[0]
    setCalcId(id)
    setForm(defaultValues(next))
    setResult(null)
    setError('')
  }

  const setField = (key, value) => setForm((prev) => ({ ...prev, [key]: value }))

  const buildParameters = () => {
    const params = { ...form }
    for (const f of calc.fields) {
      if (f.type === 'number') {
        params[f.key] = Number.parseFloat(params[f.key]) || 0
      }
      if (f.type === 'checkbox') {
        params[f.key] = Boolean(params[f.key])
      }
    }
    return params
  }

  const run = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await api.runCalculator(calc.area, calc.subtype, buildParameters())
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
          <CardTitle icon={Calculator}>Calculadora jurídica</CardTitle>
          <CardDescription>Trabalhista e cível — motor Manus via API</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <label className="block text-sm">
            Tipo de cálculo
            <select
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
              value={calcId}
              onChange={(e) => onCalcTypeChange(e.target.value)}
            >
              {CALC_TYPES.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.label}
                </option>
              ))}
            </select>
          </label>

          {calc.fields.map((field) => (
            <label key={field.key} className="block text-sm">
              {field.label}
              {field.type === 'select' && (
                <select
                  className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
                  value={form[field.key]}
                  onChange={(e) => setField(field.key, e.target.value)}
                >
                  {field.options.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              )}
              {field.type === 'checkbox' && (
                <input
                  type="checkbox"
                  className="ml-2"
                  checked={Boolean(form[field.key])}
                  onChange={(e) => setField(field.key, e.target.checked)}
                />
              )}
              {(field.type === 'number' || field.type === 'date') && (
                <input
                  type={field.type}
                  className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
                  value={form[field.key]}
                  onChange={(e) => setField(field.key, e.target.value)}
                />
              )}
              {field.hint && <span className="mt-1 block text-xs text-slate-400">{field.hint}</span>}
            </label>
          ))}

          <Button onClick={run} disabled={loading}>
            {loading ? 'Calculando...' : 'Calcular'}
          </Button>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Resultado</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {!result && <p className="text-sm text-slate-400">Preencha os campos e calcule</p>}
          {result && (
            <>
              <p className="text-2xl font-bold text-indigo-700">
                {formatMoney(result.result_value)}
              </p>
              {result.metadata?.tipo_rescisao && (
                <Badge tone="success">Rescisão: {result.metadata.tipo_rescisao}</Badge>
              )}
              {result.breakdown && (
                <div>
                  <h3 className="mb-2 text-sm font-semibold text-slate-700">Detalhamento</h3>
                  <ul className="max-h-48 space-y-1 overflow-y-auto text-sm">
                    {Object.entries(result.breakdown).map(([key, val]) => (
                      <li key={key} className="flex justify-between rounded bg-slate-50 px-2 py-1">
                        <span className="text-slate-600">{key.replace(/_/g, ' ')}</span>
                        <span className="font-medium">
                          {typeof val === 'number' ? formatMoney(val) : String(val)}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {result.formulas_used?.length > 0 && (
                <div>
                  <h3 className="mb-2 text-sm font-semibold text-slate-700">Fórmulas</h3>
                  <ul className="list-inside list-disc text-xs text-slate-600">
                    {result.formulas_used.map((f, i) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                </div>
              )}
              {result.legal_basis?.length > 0 && (
                <div>
                  <h3 className="mb-2 text-sm font-semibold text-slate-700">Base legal</h3>
                  <ul className="list-inside list-disc text-xs text-slate-600">
                    {result.legal_basis.map((b, i) => (
                      <li key={i}>{b}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
