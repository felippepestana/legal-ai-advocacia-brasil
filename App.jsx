import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { FileText, Brain, Workflow, CheckCircle, Clock, AlertTriangle, Upload, Play, Settings } from 'lucide-react'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('document-analysis')
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [workflowStatus, setWorkflowStatus] = useState('idle')

  // Simular análise de documento
  const simulateDocumentAnalysis = () => {
    setAnalysisProgress(0)
    const interval = setInterval(() => {
      setAnalysisProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          return 100
        }
        return prev + 10
      })
    }, 200)
  }

  // Simular execução de workflow
  const simulateWorkflowExecution = () => {
    setWorkflowStatus('running')
    setTimeout(() => {
      setWorkflowStatus('completed')
    }, 3000)
  }

  // Dados de exemplo para demonstração
  const analysisResults = {
    documentType: 'Petição Inicial',
    confidence: 0.85,
    entities: [
      { type: 'CPF', value: '123.456.789-00', confidence: 0.95 },
      { type: 'CNPJ', value: '12.345.678/0001-90', confidence: 0.92 },
      { type: 'Valor', value: 'R$ 50.000,00', confidence: 0.98 },
      { type: 'Data', value: '15/01/2024', confidence: 0.90 }
    ],
    opportunities: [
      { type: 'Recurso', probability: 0.75, description: 'Possível recurso de apelação' },
      { type: 'Execução', probability: 0.60, description: 'Viabilidade de execução' }
    ],
    summary: 'Ação de cobrança movida por João da Silva contra Empresa XYZ LTDA no valor de R$ 50.000,00 referente a contrato de prestação de serviços inadimplido.'
  }

  const workflows = [
    {
      id: 1,
      name: 'Análise Automática de Petição',
      description: 'Analisa automaticamente petições e cria tarefas',
      triggers: 1,
      actions: 3,
      executions: 5,
      status: 'active'
    },
    {
      id: 2,
      name: 'Lembrete de Prazo',
      description: 'Envia alertas quando prazos estão próximos',
      triggers: 1,
      actions: 2,
      executions: 12,
      status: 'active'
    },
    {
      id: 3,
      name: 'Onboarding de Cliente',
      description: 'Processo automatizado para novos clientes',
      triggers: 1,
      actions: 3,
      executions: 8,
      status: 'active'
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Plataforma Jurídica com IA
          </h1>
          <p className="text-lg text-gray-600">
            Demonstração das funcionalidades de análise inteligente de documentos e automação de fluxos de trabalho
          </p>
        </div>

        {/* Navigation Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-8">
            <TabsTrigger value="document-analysis" className="flex items-center gap-2">
              <Brain className="w-4 h-4" />
              Análise de Documentos
            </TabsTrigger>
            <TabsTrigger value="workflow-automation" className="flex items-center gap-2">
              <Workflow className="w-4 h-4" />
              Automação de Fluxos
            </TabsTrigger>
          </TabsList>

          {/* Document Analysis Tab */}
          <TabsContent value="document-analysis" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Upload Section */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Upload className="w-5 h-5" />
                    Upload de Documento
                  </CardTitle>
                  <CardDescription>
                    Faça upload de documentos processuais para análise automática
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                    <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-4">
                      Arraste arquivos aqui ou clique para selecionar
                    </p>
                    <Button onClick={simulateDocumentAnalysis}>
                      Simular Análise
                    </Button>
                  </div>
                  
                  {analysisProgress > 0 && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Analisando documento...</span>
                        <span>{analysisProgress}%</span>
                      </div>
                      <Progress value={analysisProgress} className="w-full" />
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Analysis Results */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Brain className="w-5 h-5" />
                    Resultados da Análise
                  </CardTitle>
                  <CardDescription>
                    Informações extraídas automaticamente pelo sistema de IA
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">Tipo de Documento:</span>
                    <Badge variant="secondary">{analysisResults.documentType}</Badge>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="font-medium">Confiança:</span>
                    <Badge variant="outline">{(analysisResults.confidence * 100).toFixed(0)}%</Badge>
                  </div>

                  <div>
                    <h4 className="font-medium mb-2">Entidades Extraídas:</h4>
                    <div className="space-y-2">
                      {analysisResults.entities.map((entity, index) => (
                        <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                          <span className="text-sm">
                            <strong>{entity.type}:</strong> {entity.value}
                          </span>
                          <Badge variant="outline" className="text-xs">
                            {(entity.confidence * 100).toFixed(0)}%
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium mb-2">Oportunidades Identificadas:</h4>
                    <div className="space-y-2">
                      {analysisResults.opportunities.map((opp, index) => (
                        <div key={index} className="p-3 border rounded-lg">
                          <div className="flex justify-between items-center mb-1">
                            <span className="font-medium">{opp.type}</span>
                            <Badge variant="secondary">
                              {(opp.probability * 100).toFixed(0)}%
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-600">{opp.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Summary Section */}
            <Card>
              <CardHeader>
                <CardTitle>Resumo do Documento</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 leading-relaxed">
                  {analysisResults.summary}
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Workflow Automation Tab */}
          <TabsContent value="workflow-automation" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Workflows List */}
              <div className="lg:col-span-2 space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Workflow className="w-5 h-5" />
                      Workflows Ativos
                    </CardTitle>
                    <CardDescription>
                      Fluxos de trabalho automatizados configurados no sistema
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {workflows.map((workflow) => (
                        <div key={workflow.id} className="border rounded-lg p-4">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <h3 className="font-medium">{workflow.name}</h3>
                              <p className="text-sm text-gray-600">{workflow.description}</p>
                            </div>
                            <Badge 
                              variant={workflow.status === 'active' ? 'default' : 'secondary'}
                            >
                              {workflow.status}
                            </Badge>
                          </div>
                          
                          <div className="grid grid-cols-3 gap-4 mt-3 text-sm">
                            <div className="text-center">
                              <div className="font-medium">{workflow.triggers}</div>
                              <div className="text-gray-500">Gatilhos</div>
                            </div>
                            <div className="text-center">
                              <div className="font-medium">{workflow.actions}</div>
                              <div className="text-gray-500">Ações</div>
                            </div>
                            <div className="text-center">
                              <div className="font-medium">{workflow.executions}</div>
                              <div className="text-gray-500">Execuções</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Workflow Execution */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Play className="w-5 h-5" />
                    Executar Workflow
                  </CardTitle>
                  <CardDescription>
                    Teste a execução de workflows
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button 
                    onClick={simulateWorkflowExecution}
                    disabled={workflowStatus === 'running'}
                    className="w-full"
                  >
                    {workflowStatus === 'running' ? 'Executando...' : 'Simular Execução'}
                  </Button>

                  {workflowStatus !== 'idle' && (
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        {workflowStatus === 'running' && (
                          <>
                            <Clock className="w-4 h-4 text-blue-500 animate-spin" />
                            <span className="text-sm">Executando workflow...</span>
                          </>
                        )}
                        {workflowStatus === 'completed' && (
                          <>
                            <CheckCircle className="w-4 h-4 text-green-500" />
                            <span className="text-sm">Workflow concluído!</span>
                          </>
                        )}
                      </div>

                      <div className="space-y-2 text-sm">
                        <div className="flex items-center gap-2">
                          <CheckCircle className="w-3 h-3 text-green-500" />
                          <span>Documento analisado</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <CheckCircle className="w-3 h-3 text-green-500" />
                          <span>Tarefa criada</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <CheckCircle className="w-3 h-3 text-green-500" />
                          <span>Notificação enviada</span>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Workflow Builder Preview */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  Construtor de Workflows
                </CardTitle>
                <CardDescription>
                  Interface visual para criar e editar fluxos de trabalho personalizados
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-gray-50 rounded-lg p-6 text-center">
                  <div className="flex items-center justify-center space-x-4 mb-4">
                    <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Upload className="w-8 h-8 text-blue-600" />
                    </div>
                    <div className="w-8 h-1 bg-gray-300"></div>
                    <div className="w-16 h-16 bg-green-100 rounded-lg flex items-center justify-center">
                      <Brain className="w-8 h-8 text-green-600" />
                    </div>
                    <div className="w-8 h-1 bg-gray-300"></div>
                    <div className="w-16 h-16 bg-purple-100 rounded-lg flex items-center justify-center">
                      <CheckCircle className="w-8 h-8 text-purple-600" />
                    </div>
                  </div>
                  <p className="text-gray-600">
                    Interface drag-and-drop para criar workflows personalizados
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

