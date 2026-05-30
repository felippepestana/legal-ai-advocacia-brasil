"""Smoke tests — executar na raiz: python -m pytest tests/test_smoke.py -q"""

from datetime import date

import services.api.bootstrap  # noqa: F401

from legal_core.validators import validate_peticao_inicial
from services.api.adapters.deadlines import calculate_deadline
from services.api.adapters.documents import analyze_document_text


def test_analyze_returns_schema_keys():
    text = (
        "EXCELENTISSIMO SENHOR DOUTOR JUIZ. JOAO, CPF 123.456.789-00. "
        "DOS FATOS. DO DIREITO. DOS PEDIDOS. Valor da causa. OAB/SP 1."
    )
    result = analyze_document_text(text)
    for key in ("document_type", "summary", "entities", "metadata"):
        assert key in result
    assert result["metadata"]["disclaimer"]


def test_validate_peticao_scores():
    text = "Excelentissimo Juiz. CPF. DOS FATOS. DOS PEDIDOS. valor da causa. OAB"
    result = validate_peticao_inicial(text)
    assert 0 <= result.compliance_score <= 100
    assert len(result.itens) >= 5


def test_deadline_contestacao():
    result = calculate_deadline(date(2026, 5, 20), "contestacao", "estadual")
    assert result["business_days"] == 15
    assert result["calculated_date"] > "2026-05-20"


def test_calculator_rescisao():
    from services.api.adapters.calculator import run_calculation

    result = run_calculation(
        "trabalhista",
        "rescisao",
        {
            "salario": 3000.0,
            "data_admissao": "2022-01-15",
            "data_demissao": "2024-09-15",
            "tipo_rescisao": "sem_justa_causa",
            "aviso_previo_trabalhado": False,
        },
    )
    assert float(result["result_value"]) > 0
    assert "breakdown" in result


def test_search_returns_results():
    from services.api.adapters.search import run_search

    result = run_search("danos morais negativação", use_external_sources=False)
    assert result["total_results"] >= 1
    assert len(result["results"]) >= 1
    assert result["results"][0]["title"]


def test_search_external_datajud():
    from services.api.adapters.search import run_search

    result = run_search(
        "danos morais",
        "jurisprudencia",
        use_external_sources=True,
        tribunals=["stj"],
    )
    assert result["total_results"] >= 1
    assert "sources" in result


def test_search_legislacao_lei(monkeypatch):
    from legal_sources.base import SearchHit
    from services.api.adapters.search import run_search

    def fake_senado(query):
        return (
            [
                SearchHit(
                    id="lei-8078",
                    title="Lei 8078/1990 - Código de Defesa do Consumidor",
                    content="CDC",
                    source="Senado",
                    provider="senado_legislacao",
                    relevance_score=0.95,
                )
            ],
            [],
        )

    monkeypatch.setattr("legal_sources.aggregator.search_senado_legislacao", fake_senado)
    monkeypatch.setattr("legal_sources.aggregator.search_lexml_sru", lambda *a, **k: ([], []))
    monkeypatch.setattr("legal_sources.aggregator.search_datajud", lambda *a, **k: ([], []))
    monkeypatch.setattr("legal_sources.aggregator.search_jurisprudencias", lambda *a, **k: ([], []))

    result = run_search(
        "lei 8078 consumidor",
        "legislacao",
        use_external_sources=True,
    )
    providers = result.get("sources", {}).get("providers", [])
    assert result["total_results"] >= 1
    assert "senado_legislacao" in providers or any(
        "8078" in (r.get("title") or "") for r in result["results"]
    )


def test_generate_procuracao():
    from services.api.adapters.generation import generate_document

    doc = generate_document(
        "procuracao",
        {
            "outorgante": {"nome": "Maria", "qualificacao": "brasileira"},
            "outorgado": {"nome": "João", "estado": "SP", "oab": "123456", "endereco": "SP"},
            "poderes": "Ad judicia et extra.",
        },
    )
    assert "PROCURAÇÃO" in doc["content"]
    assert doc["quality_score"] > 0


def test_assistant_chat():
    from services.api.adapters.assistant import chat

    result = chat("O que são danos morais?", user_level="advogado")
    assert len(result["answer"]) > 20
    assert result["disclaimer"]


def test_workflow_templates():
    from services.api.adapters.workflows import list_templates

    templates = list_templates()
    assert len(templates) >= 1
    assert templates[0]["id"]


def test_workflow_persistence(tmp_path, monkeypatch):
    import services.api.adapters.workflows as wf

    store_file = tmp_path / "wf.json"
    monkeypatch.setenv("WORKFLOW_STORE_PATH", str(store_file))
    wf._engine = None
    wf._engine_loaded = False

    created = wf.create_from_template("peticao_inicial", "Teste persistência", {})
    assert store_file.is_file()

    wf._engine = None
    wf._engine_loaded = False
    wf2 = wf.get_engine()
    assert created["workflow_id"] in wf2.workflows


def test_analytics_performance():
    from services.api.adapters.analytics import run_analysis

    report = run_analysis("performance", num_cases=80)
    assert report["analysis_type"] == "Performance"
    assert "metrics" in report
    assert len(report.get("insights", [])) >= 1
