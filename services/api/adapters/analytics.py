from __future__ import annotations

import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import services.api.bootstrap  # noqa: F401

from enhanced_analytics_engine import AnalyticsReport, EnhancedAnalyticsEngine

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CHARTS_DIR = PROJECT_ROOT / "data" / "analytics" / "charts"

ANALYSIS_HANDLERS = {
    "performance": "generate_performance_analysis",
    "predictive": "generate_predictive_analysis",
    "financial": "generate_financial_analysis",
}


def list_analysis_types() -> list[dict[str, str]]:
    return [
        {"id": "performance", "label": "Performance", "description": "Taxa de sucesso, prazos e receita por área"},
        {"id": "predictive", "label": "Preditiva", "description": "Tendências e projeção de volume"},
        {"id": "financial", "label": "Financeira", "description": "Receita, custos e margem por área"},
    ]


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, AttributeError):
            pass
    if isinstance(value, float) and (value != value):  # NaN
        return None
    return value


def _report_to_dict(report: AnalyticsReport) -> dict[str, Any]:
    start, end = report.data_period
    return {
        "id": report.id,
        "title": report.title,
        "analysis_type": report.analysis_type.value,
        "generated_at": report.generated_at.isoformat(),
        "data_period": {
            "start": _json_safe(start),
            "end": _json_safe(end),
        },
        "metrics": _json_safe(report.metrics),
        "insights": report.insights,
        "recommendations": report.recommendations,
        "charts": report.charts,
        "metadata": {"synthetic_data": True},
    }


def charts_directory() -> Path:
    raw = os.environ.get("ANALYTICS_CHARTS_DIR", "").strip()
    return Path(raw) if raw else DEFAULT_CHARTS_DIR


def _export_charts_from_metrics(report: dict[str, Any]) -> list[str]:
    """Gera PNGs a partir das métricas (sem paths legados /home/ubuntu)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    metrics = report.get("metrics") or {}
    out_dir = charts_directory() / report["id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[str] = []

    def bar_chart(data: dict[str, float], filename: str, title: str, ylabel: str) -> None:
        if not data:
            return
        fig, ax = plt.subplots(figsize=(10, 5))
        keys = list(data.keys())
        values = [float(data[k]) for k in keys]
        ax.bar(keys, values, color="steelblue", edgecolor="navy", alpha=0.8)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        plt.xticks(rotation=35, ha="right")
        plt.tight_layout()
        path = out_dir / filename
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        saved.append(str(path.relative_to(PROJECT_ROOT)))

    bar_chart(
        metrics.get("success_rate_by_area") or {},
        "success_rate_by_area.png",
        "Taxa de sucesso por área (%)",
        "%",
    )
    bar_chart(
        metrics.get("revenue_by_area") or {},
        "revenue_by_area.png",
        "Receita por área",
        "R$",
    )

    return saved


@lru_cache(maxsize=1)
def get_engine() -> EnhancedAnalyticsEngine:
    engine = EnhancedAnalyticsEngine()
    engine._generate_performance_charts = lambda _df, _m: []  # type: ignore[method-assign]
    engine._generate_predictive_charts = lambda _df, _m: []  # type: ignore[method-assign]
    engine._generate_financial_charts = lambda _df, _m: []  # type: ignore[method-assign]
    return engine


def run_analysis(
    analysis_type: str,
    num_cases: int = 500,
    *,
    export_charts: bool = False,
) -> dict[str, Any]:
    handler_name = ANALYSIS_HANDLERS.get(analysis_type.lower())
    if not handler_name:
        raise ValueError(
            f"Tipo de análise inválido: {analysis_type}. "
            f"Use: {', '.join(ANALYSIS_HANDLERS)}"
        )

    num_cases = max(50, min(num_cases, 2000))
    engine = get_engine()
    engine.load_data(engine.data_generator.generate_case_data(num_cases))

    handler = getattr(engine, handler_name)
    report = handler()
    payload = _report_to_dict(report)
    if export_charts:
        payload["charts"] = _export_charts_from_metrics(payload)
        payload["metadata"]["charts_exported"] = bool(payload["charts"])
        payload["chart_urls"] = [
            {"name": Path(p).name, "path": p, "url": f"/v1/analytics/charts/{Path(p).name}"}
            for p in payload["charts"]
        ]
    return payload


def resolve_chart_file(filename: str) -> Path | None:
    safe = Path(filename).name
    if safe != filename:
        return None
    base = charts_directory()
    for path in base.rglob(safe):
        if path.is_file():
            return path
    return None
