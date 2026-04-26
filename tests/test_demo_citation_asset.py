from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable

from src.citation_linking import find_section_for_citation


ROOT = Path(__file__).resolve().parents[1]
DEMO_JSON_PATH = ROOT / "assets" / "demo" / "demo.json"
DEMO_SECTION_TEXT_PATH = ROOT / "assets" / "demo" / "section_text.json"


def _iter_demo_citations(report: Dict[str, Any]) -> Iterable[str]:
    for field in ("coverage_highlights", "exclusions_limitations", "denial_reasons"):
        for item in report.get(field, []) or []:
            citation = str(item.get("citation", "") or "").strip()
            if citation:
                yield citation

    for angle in report.get("dispute_angles", []) or []:
        for citation in angle.get("citations", []) or []:
            citation = str(citation).strip()
            if citation:
                yield citation


def test_demo_section_text_asset_links_all_demo_report_citations():
    demo_report = json.loads(DEMO_JSON_PATH.read_text(encoding="utf-8"))
    section_map = json.loads(DEMO_SECTION_TEXT_PATH.read_text(encoding="utf-8"))

    missing = [
        citation
        for citation in _iter_demo_citations(demo_report)
        if find_section_for_citation(citation, section_map) is None
    ]

    assert missing == []


def test_demo_section_text_asset_is_sanitized():
    section_map = json.loads(DEMO_SECTION_TEXT_PATH.read_text(encoding="utf-8"))

    assert section_map
    for section_text in section_map.values():
        normalized = section_text.lower()
        assert "demo-safe source excerpt" in normalized
        assert "not raw client policy text" in normalized
