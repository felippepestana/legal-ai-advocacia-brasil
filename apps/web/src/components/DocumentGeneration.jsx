import { useEffect, useState } from 'react'
import { FileOutput, Sparkles } from 'lucide-react'
import { api } from '../api/client'
import { Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui'

const SAMPLE_PROCURACAO = {
  outorgante: {
    nome: 'Maria da Silva',
    qualificacao: 'brasileira, casada, empresária, CPF 123.456.789-00',
  },
  outorgado: {
    nome: 'Dr. João Advogado',
    estado: 'SP',
    oab: '123456',
    endereco: 'Rua Example, 100, São Paulo/SP',
  },
  poderes:
    'Representar a outorgante em juízo ou fora dele, com poderes da cláusula ad judicia et extra, podendo propor ações, contestar, transigir, receber e dar quitação.',
}

const SAMPLE_PETICAO = {
  autor: {
    nome: 'Carlos Souza',
    nacionalidade: 'brasileiro',
    estado_civil: 'solteiro',
    profissao: 'analista',
    cpf: '987.654.321-00',
    endereco: 'Av. Paulista, 1000, São Paulo/SP',
  },
  reu: { nome: 'Empresa XYZ Ltda', qualificacao: 'pessoa jurídica, CNPJ 12.345.678/0001-90' },
  fatos: 'O autor contratou serviços que não foram prestados conforme acordado, causando prejuízo material.',
  fundamentacao_juridica: 'Aplica-se o Código Civil e o CDC quanto à responsabilidade contratual.',
  pedidos: ['Condenação ao pagamento de R$ 15.000,00', 'Citação do réu', 'Condenação em custas e honorários'],
  valor_causa: '15.000,00',
  advogado: { nome: 'Dr. João Advogado', estado: 'SP', numero: '123456' },
  tipo_acao: 'AÇÃO DE COBRANÇA',
}

export default function DocumentGeneration({ geminiAvailable }) {
  const [templates, setTemplates] = useState([])
  const [templateId, setTemplateId] = useState('procuracao')
  const [jsonData, setJsonData] = useState(JSON.stringify(SAMPLE_PROCURACAO, null, 2))
  const [useGemini, setUseGemini] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  useEffect(() => {
    api.listTemplates().then((r) => {
      setTemplates(r.templates || [])
    }).catch(() => {})
  }, [])

  const loadSample = () => {
    if (templateId === 'peticao_inicial_civil') {
      setJsonData(JSON.stringify(SAMPLE_PETICAO, null, 2))
    } else {
      setJsonData(JSON.stringify(SAMPLE_PROCURACAO, null, 2))
    }
  }

  const generate = async () => {
    let data
    try {
      data = JSON.parse(jsonData)
    } catch {
      setError('JSON inválido nos dados estruturados.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const doc = await api.generateDocument(templateId, data, useGemini)
      setResult(doc)
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
          <CardTitle icon={FileOutput}>Geração de peças</CardTitle>
          <CardDescription>Templates Jinja2 + enriquecimento opcional Gemini</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <select
            className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
            value={templateId}
            onChange={(e) => {
              setTemplateId(e.target.value)
              setResult(null)
            }}
          >
            {templates.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
          {templates.find((t) => t.id === templateId) && (
            <p className="text-xs text-slate-500">
              Campos: {templates.find((t) => t.id === templateId).required_fields.join(', ')}
            </p>
          )}
          <textarea
            className="min-h-[280px] w-full rounded-lg border border-slate-200 p-3 font-mono text-xs"
            value={jsonData}
            onChange={(e) => setJsonData(e.target.value)}
          />
          <div className="flex flex-wrap gap-3">
            <Button variant="outline" onClick={loadSample}>
              Carregar exemplo
            </Button>
            {geminiAvailable && (
              <label className="flex items-center gap-2 text-sm text-slate-600">
                <input type="checkbox" checked={useGemini} onChange={(e) => setUseGemini(e.target.checked)} />
                <Sparkles className="h-4 w-4 text-amber-500" />
                Enriquecer com Gemini
              </label>
            )}
          </div>
          <Button onClick={generate} disabled={loading}>
            {loading ? 'Gerando...' : 'Gerar minuta'}
          </Button>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Minuta gerada</CardTitle>
        </CardHeader>
        <CardContent>
          {!result && <p className="text-sm text-slate-400">Aguardando geração</p>}
          {result && (
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                <Badge>{result.template_name}</Badge>
                <Badge tone="success">Qualidade {(result.quality_score * 100).toFixed(0)}%</Badge>
                {result.metadata?.ai_enhanced && <Badge tone="warning">Gemini</Badge>}
              </div>
              <pre className="max-h-[480px] overflow-y-auto whitespace-pre-wrap rounded-lg bg-slate-50 p-4 text-xs text-slate-800">
                {result.content}
              </pre>
              <p className="text-xs text-slate-400">{result.metadata?.disclaimer}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
