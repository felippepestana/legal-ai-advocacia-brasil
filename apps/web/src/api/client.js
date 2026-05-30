const API_BASE = import.meta.env.VITE_API_URL ?? ''
const API_KEY_STORAGE = 'legal_platform_api_key'

export function getStoredApiKey() {
  try {
    return localStorage.getItem(API_KEY_STORAGE) || ''
  } catch {
    return ''
  }
}

export function setStoredApiKey(key) {
  try {
    if (key) localStorage.setItem(API_KEY_STORAGE, key)
    else localStorage.removeItem(API_KEY_STORAGE)
  } catch {
    /* ignore */
  }
}

function authHeaders() {
  const key = getStoredApiKey()
  return key ? { 'X-API-Key': key } : {}
}

async function requestBlob(path) {
  const res = await fetch(`${API_BASE}${path}`, { headers: { ...authHeaders() } })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || data.message || `Erro ${res.status}`)
  }
  return res.blob()
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...authHeaders(), ...options.headers },
    ...options,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(data.detail || data.message || `Erro ${res.status}`)
  }
  return data
}

export const api = {
  health: () => request('/v1/health'),
  legalAreas: () => request('/v1/ontology/legal-areas'),
  auditRecent: (limit = 20) => request(`/v1/audit/recent?limit=${limit}`),
  auditExportCsv: async (limit = 500) => {
    const blob = await requestBlob(`/v1/audit/export?limit=${limit}`)
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `auditoria_ia_${new Date().toISOString().slice(0, 10)}.csv`
    anchor.click()
    URL.revokeObjectURL(url)
  },
  analyzeDocument: (text, legalArea, enhanceWithGemini) =>
    request('/v1/documents/analyze', {
      method: 'POST',
      body: JSON.stringify({
        text,
        legal_area: legalArea || null,
        enhance_with_gemini: enhanceWithGemini,
      }),
    }),
  validateDocument: (text, tipoPeca = 'peticao_inicial') =>
    request('/v1/documents/validate', {
      method: 'POST',
      body: JSON.stringify({ text, tipo_peca: tipoPeca }),
    }),
  calculateDeadline: (eventDate, deadlineType, courtType = 'estadual') =>
    request('/v1/deadlines/calculate', {
      method: 'POST',
      body: JSON.stringify({
        event_date: eventDate,
        deadline_type: deadlineType,
        court_type: courtType,
      }),
    }),
  runCalculator: (area, subtype, parameters) =>
    request('/v1/calculator/run', {
      method: 'POST',
      body: JSON.stringify({ area, subtype, parameters }),
    }),
  searchLegal: (query, searchType, synthesizeWithGemini, useExternalSources = true, tribunals = []) =>
    request('/v1/search/query', {
      method: 'POST',
      body: JSON.stringify({
        query,
        search_type: searchType,
        synthesize_with_gemini: synthesizeWithGemini,
        use_external_sources: useExternalSources,
        tribunals,
      }),
    }),
  listTemplates: () => request('/v1/generation/templates'),
  generateDocument: (templateId, data, aiEnhancement) =>
    request('/v1/generation/generate', {
      method: 'POST',
      body: JSON.stringify({
        template_id: templateId,
        data,
        ai_enhancement: aiEnhancement,
      }),
    }),
  listWorkflowTemplates: () => request('/v1/workflows/templates'),
  createWorkflow: (templateId, name, variables) =>
    request('/v1/workflows/create', {
      method: 'POST',
      body: JSON.stringify({ template_id: templateId, name, variables }),
    }),
  executeWorkflow: (workflowId, context) =>
    request('/v1/workflows/execute', {
      method: 'POST',
      body: JSON.stringify({ workflow_id: workflowId, context }),
    }),
  getWorkflowExecution: (executionId) => request(`/v1/workflows/executions/${executionId}`),
  assistantChat: (message, userLevel, enhanceWithGemini) =>
    request('/v1/assistant/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        user_level: userLevel,
        enhance_with_gemini: enhanceWithGemini,
      }),
    }),
  listAnalyticsTypes: () => request('/v1/analytics/types'),
  runAnalytics: (analysisType, numCases = 500, exportCharts = false) =>
    request('/v1/analytics/run', {
      method: 'POST',
      body: JSON.stringify({
        analysis_type: analysisType,
        num_cases: numCases,
        export_charts: exportCharts,
      }),
    }),
}
