import { useState } from 'react'
import { Brain, FileText, Sparkles, Upload } from 'lucide-react'
import { api } from '../api/client'
import { Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui'

const SAMPLE = `EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA 1ª VARA CÍVEL DA COMARCA DE SÃO PAULO

JOÃO DA SILVA, brasileiro, casado, empresário, CPF nº 123.456.789-10,
por seu advogado que esta subscreve, OAB/SP 123456, vem propor

AÇÃO DE COBRANÇA

em face de BANCO XYZ S.A., CNPJ 12.345.678/0001-90.

DOS FATOS
O autor manteve relação contratual com o réu, que inscreveu indevidamente seu nome nos órgãos de proteção ao crédito.

DO DIREITO
Aplica-se o CDC e o Código Civil.

DOS PEDIDOS
a) Condenação ao pagamento de R$ 50.000,00;
b) Valor da causa: R$ 50.000,00.
Provas: documentos e testemunhas.
Opta pela audiência de conciliação.

São Paulo, 12 de setembro de 2024.`

export default function DocumentAnalysis({ geminiAvailable, legalAreas }) {
  const [text, setText] = useState('')
  const [legalArea, setLegalArea] = useState('')
  const [useGemini, setUseGemini] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const runAnalysis = async () => {
    if (text.trim().length < 20) {
      setError('Informe pelo menos 20 caracteres de texto.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const data = await api.analyzeDocument(text, legalArea || null, useGemini)
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
          <CardTitle icon={Upload}>Documento</CardTitle>
          <CardDescription>Cole o texto da peça ou carregue um .txt</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <textarea
            className="min-h-[280px] w-full rounded-lg border border-slate-200 p-3 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            placeholder="Cole aqui o conteúdo do documento jurídico..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <div className="flex flex-wrap gap-3">
            <select
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
              value={legalArea}
              onChange={(e) => setLegalArea(e.target.value)}
            >
              <option value="">Área (opcional)</option>
              {legalAreas.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
            {geminiAvailable && (
              <label className="flex items-center gap-2 text-sm text-slate-600">
                <input
                  type="checkbox"
                  checked={useGemini}
                  onChange={(e) => setUseGemini(e.target.checked)}
                />
                <Sparkles className="h-4 w-4 text-amber-500" />
                Enriquecer com Gemini
              </label>
            )}
          </div>
          <div className="flex gap-2">
            <Button onClick={runAnalysis} disabled={loading}>
              {loading ? 'Analisando...' : 'Analisar documento'}
            </Button>
            <Button variant="outline" onClick={() => setText(SAMPLE)}>
              Exemplo
            </Button>
          </div>
          <label className="block text-sm text-slate-500">
            <span className="mb-1 block">Ou envie arquivo .txt</span>
            <input
              type="file"
              accept=".txt"
              className="text-sm"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (!file) return
                const reader = new FileReader()
                reader.onload = () => setText(String(reader.result || ''))
                reader.readAsText(file)
              }}
            />
          </label>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle icon={Brain}>Resultado</CardTitle>
          <CardDescription>Análise estruturada + lacunas CPC quando aplicável</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!result && (
            <div className="flex flex-col items-center py-12 text-slate-400">
              <FileText className="mb-3 h-12 w-12" />
              <p className="text-sm">Execute uma análise para ver os resultados</p>
            </div>
          )}
          {result && (
            <>
              <div className="flex flex-wrap gap-2">
                <Badge>{result.document_type}</Badge>
                {result.legal_area && <Badge tone="success">{result.legal_area}</Badge>}
                <Badge tone={result.confidence >= 0.7 ? 'success' : 'warning'}>
                  Confiança {(result.confidence * 100).toFixed(0)}%
                </Badge>
                {result.metadata?.ai_enhanced && (
                  <Badge tone="warning">Gemini</Badge>
                )}
              </div>
              <div>
                <h3 className="mb-1 text-sm font-semibold text-slate-700">Resumo</h3>
                <p className="text-sm text-slate-600">{result.summary}</p>
              </div>
              {result.entities?.length > 0 && (
                <div>
                  <h3 className="mb-2 text-sm font-semibold text-slate-700">Entidades</h3>
                  <ul className="space-y-1 text-sm">
                    {result.entities.map((e, i) => (
                      <li key={i} className="flex justify-between rounded bg-slate-50 px-2 py-1">
                        <span className="font-medium text-slate-600">{e.type}</span>
                        <span>{e.text}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {result.gaps?.length > 0 && (
                <div>
                  <h3 className="mb-2 text-sm font-semibold text-amber-800">Lacunas / CPC</h3>
                  <ul className="list-inside list-disc text-sm text-amber-900">
                    {result.gaps.map((g, i) => (
                      <li key={i}>{g}</li>
                    ))}
                  </ul>
                </div>
              )}
              <p className="border-t pt-3 text-xs text-slate-400">
                {result.metadata?.disclaimer}
              </p>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
