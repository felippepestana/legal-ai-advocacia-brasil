from __future__ import annotations

import logging
import xml.etree.ElementTree as ET

import requests

from legal_sources.base import SearchHit

logger = logging.getLogger(__name__)

SRU_CANDIDATES = (
    "https://www.lexml.gov.br/busca/SRU",
    "https://www.lexml.gov.br/SRU",
)


def search_lexml_sru(query: str, *, max_records: int = 5, timeout: int = 15) -> tuple[list[SearchHit], list[str]]:
    """
    Tenta SRU do LexML. Em muitos ambientes o endpoint /busca/SRU retorna 404;
    nesse caso retorna lista vazia e o agregador usa Senado/Dados Abertos.
    """
    warnings: list[str] = []
    hits: list[SearchHit] = []
    cql = f'dc.anywhere "{query[:120]}"'

    for base_url in SRU_CANDIDATES:
        try:
            response = requests.get(
                base_url,
                params={
                    "operation": "searchRetrieve",
                    "version": "1.1",
                    "query": cql,
                    "maximumRecords": str(max_records),
                },
                timeout=timeout,
            )
            if response.status_code == 404:
                continue
            if not response.ok:
                warnings.append(f"LexML SRU: HTTP {response.status_code}")
                continue
            hits = _parse_sru_xml(response.text)
            if hits:
                return hits, warnings
        except requests.RequestException as exc:
            logger.debug("LexML SRU %s: %s", base_url, exc)

    if not hits:
        warnings.append(
            "LexML SRU indisponível neste ambiente; legislação via API Senado (rede LexML)."
        )
    return hits, warnings


def _parse_sru_xml(xml_text: str) -> list[SearchHit]:
    hits: list[SearchHit] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return hits

    ns = {"srw": "http://www.loc.gov/zing/srw/", "dc": "http://purl.org/dc/elements/1.1/"}
    for record in root.findall(".//srw:record", ns):
        title_el = record.find(".//dc:title", ns)
        desc_el = record.find(".//dc:description", ns)
        title = (title_el.text if title_el is not None else "Documento LexML") or "Documento LexML"
        content = (desc_el.text if desc_el is not None else title) or title
        hits.append(
            SearchHit(
                id=f"lexml_{hash(title) % 10**8}",
                title=title.strip(),
                content=content.strip()[:2000],
                source="LexML Brasil",
                provider="lexml",
                url="https://www.lexml.gov.br/",
                relevance_score=0.75,
            )
        )
    return hits
