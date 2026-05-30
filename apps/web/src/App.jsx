import { useEffect, useState } from 'react'
import {
  BarChart3,
  Bot,
  Brain,
  Calculator,
  Calendar,
  ClipboardList,
  FileOutput,
  GitBranch,
  Scale,
  Search,
} from 'lucide-react'
import { api } from './api/client'
import DocumentAnalysis from './components/DocumentAnalysis'
import DeadlineCalculator from './components/DeadlineCalculator'
import DocumentValidate from './components/DocumentValidate'
import LegalCalculator from './components/LegalCalculator'
import LegalSearch from './components/LegalSearch'
import DocumentGeneration from './components/DocumentGeneration'
import AssistantChat from './components/AssistantChat'
import WorkflowRunner from './components/WorkflowRunner'
import LegalAnalytics from './components/LegalAnalytics'
import AuditPanel from './components/AuditPanel'

const TABS = [
  { id: 'analysis', label: 'Análise', icon: Brain },
  { id: 'validate', label: 'CPC', icon: Scale },
  { id: 'deadlines', label: 'Prazos', icon: Calendar },
  { id: 'calculator', label: 'Cálculos', icon: Calculator },
  { id: 'search', label: 'Pesquisa', icon: Search },
  { id: 'generation', label: 'Peças', icon: FileOutput },
  { id: 'workflows', label: 'Workflows', icon: GitBranch },
  { id: 'assistant', label: 'Assistente', icon: Bot },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'audit', label: 'Auditoria', icon: ClipboardList },
]

export default function App() {
  const [tab, setTab] = useState('analysis')
  const [health, setHealth] = useState(null)
  const [legalAreas, setLegalAreas] = useState([])
  const [apiError, setApiError] = useState('')

  useEffect(() => {
    Promise.all([api.health(), api.legalAreas()])
      .then(([h, areas]) => {
        setHealth(h)
        setLegalAreas(areas.areas || [])
      })
      .catch(() => {
        setApiError(
          'API indisponível. Inicie o backend: python -m uvicorn services.api.main:app --port 8000',
        )
      })
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 sm:text-4xl">
            Plataforma Jurídica — Advocacia Brasil
          </h1>
          <p className="mt-2 text-slate-600">
            Plataforma jurídica completa — 10 módulos integrados à API
          </p>
          <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-500">
            {health && (
              <>
                <span className="rounded-full bg-emerald-100 px-2 py-1 text-emerald-800">
                  API {health.status}
                </span>
                {health.auth_required && (
                  <span className="rounded-full bg-indigo-100 px-2 py-1 text-indigo-800">
                    Auth {health.tenants_configured} tenant(s)
                  </span>
                )}
                {health.structured_logging && (
                  <span className="rounded-full bg-sky-100 px-2 py-1 text-sky-800">
                    Logs JSON
                  </span>
                )}
                {health.sentry_enabled && (
                  <span className="rounded-full bg-violet-100 px-2 py-1 text-violet-800">
                    Sentry
                  </span>
                )}
                {health.gemini_available ? (
                  <span className="rounded-full bg-amber-100 px-2 py-1 text-amber-800">
                    IA {health.ai_backend === 'vertex' ? 'Vertex' : 'Gemini'} · {health.ai_model}
                  </span>
                ) : (
                  <span className="rounded-full bg-slate-200 px-2 py-1">
                    IA: GEMINI_API_KEY (dev) ou GOOGLE_CLOUD_PROJECT + Vertex (prod)
                  </span>
                )}
              </>
            )}
            {apiError && (
              <span className="rounded-full bg-red-100 px-2 py-1 text-red-700">{apiError}</span>
            )}
          </div>
        </header>

        <nav className="mb-6 flex flex-wrap gap-2">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => setTab(id)}
              className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition ${
                tab === id
                  ? 'bg-indigo-600 text-white shadow'
                  : 'bg-white text-slate-600 hover:bg-slate-50'
              }`}
            >
              <Icon className="h-4 w-4" />
              {label}
            </button>
          ))}
        </nav>

        {tab === 'analysis' && (
          <DocumentAnalysis
            geminiAvailable={health?.gemini_available}
            legalAreas={legalAreas}
          />
        )}
        {tab === 'validate' && <DocumentValidate />}
        {tab === 'deadlines' && <DeadlineCalculator />}
        {tab === 'calculator' && <LegalCalculator />}
        {tab === 'search' && <LegalSearch geminiAvailable={health?.gemini_available} />}
        {tab === 'generation' && (
          <DocumentGeneration geminiAvailable={health?.gemini_available} />
        )}
        {tab === 'workflows' && <WorkflowRunner />}
        {tab === 'assistant' && <AssistantChat geminiAvailable={health?.gemini_available} />}
        {tab === 'analytics' && <LegalAnalytics />}
        {tab === 'audit' && <AuditPanel health={health} />}

        <footer className="mt-12 text-center text-xs text-slate-400">
          Ferramenta de apoio — revisão por advogado habilitado obrigatória antes de protocolo.
        </footer>
      </div>
    </div>
  )
}
